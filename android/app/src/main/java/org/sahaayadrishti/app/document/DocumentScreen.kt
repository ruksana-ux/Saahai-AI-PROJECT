package org.sahaayadrishti.app.document

import android.content.Context
import android.content.Intent
import android.view.LayoutInflater
import android.view.View
import android.widget.AdapterView
import android.widget.Button
import android.widget.Spinner
import android.widget.TextView
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.ImageProxy
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.lifecycleScope
import org.sahaayadrishti.app.R
import org.sahaayadrishti.app.haptics.HapticEngine
import org.sahaayadrishti.app.settings.SettingsStore
import org.sahaayadrishti.app.speech.SpeechEngine
import org.sahaayadrishti.app.util.BitmapUtils
import org.sahaayadrishti.app.util.toSafeBitmap
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import kotlinx.coroutines.launch

/**
 * Document tab: capture one page, read it offline, speak it, optionally share.
 *
 * Sharing is the only way text leaves the phone and it is always an explicit
 * tap on a share sheet. Nothing is uploaded automatically.
 */
class DocumentScreen(
    private val context: Context,
    private val lifecycleOwner: LifecycleOwner,
    private val speech: SpeechEngine,
    private val haptics: HapticEngine,
    private val settings: SettingsStore,
) {

    val view: View = LayoutInflater.from(context).inflate(R.layout.screen_document, null)

    private val status: TextView = view.findViewById(R.id.document_status)
    private val output: TextView = view.findViewById(R.id.document_text)
    private val preview: PreviewView = view.findViewById(R.id.document_preview)
    private val scriptSpinner: Spinner = view.findViewById(R.id.document_script)
    private val captureButton: Button = view.findViewById(R.id.btn_document_capture)

    private val reader = DocumentReader()
    private val cameraExecutor: ExecutorService = Executors.newSingleThreadExecutor()
    private var imageCapture: ImageCapture? = null
    private var lastText: String = ""
    private var busy = false
    private var destroyed = false

    init {
        scriptSpinner.setSelection(settings.documentScript.coerceIn(0, 1))
        scriptSpinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                settings.documentScript = position
            }

            override fun onNothingSelected(parent: AdapterView<*>?) = Unit
        }

        captureButton.setOnClickListener { capture() }
        view.findViewById<Button>(R.id.btn_document_read).setOnClickListener {
            if (lastText.isBlank()) {
                speech.speak(context.getString(R.string.document_status_no_text))
            } else {
                speech.speak(lastText)
            }
        }
        view.findViewById<Button>(R.id.btn_document_share).setOnClickListener { share() }
        view.findViewById<Button>(R.id.btn_document_stop).setOnClickListener { speech.stop() }

        bindCamera()
    }

    fun onDestroy() {
        destroyed = true
        imageCapture = null
        reader.close()
        cameraExecutor.shutdown()
        val future = ProcessCameraProvider.getInstance(context)
        if (future.isDone) {
            runCatching { future.get().unbindAll() }
        }
    }

    private fun bindCamera() {
        val future = ProcessCameraProvider.getInstance(context)
        future.addListener({
            // The tab can be closed before the provider future resolves.
            if (destroyed) return@addListener
            try {
                val provider = future.get()
                val cameraPreview = Preview.Builder().build().also {
                    it.setSurfaceProvider(preview.surfaceProvider)
                }
                val capture = ImageCapture.Builder()
                    .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                    .build()
                imageCapture = capture
                provider.unbindAll()
                provider.bindToLifecycle(
                    lifecycleOwner,
                    CameraSelector.DEFAULT_BACK_CAMERA,
                    cameraPreview,
                    capture,
                )
            } catch (error: Throwable) {
                status.text = context.getString(R.string.error_generic)
                android.util.Log.e("DocumentScreen", "camera bind failed", error)
            }
        }, ContextCompat.getMainExecutor(context))
    }

    private fun capture() {
        if (destroyed) return
        val capture = imageCapture ?: return
        if (busy) return
        busy = true
        captureButton.isEnabled = false
        status.text = context.getString(R.string.document_status_reading)
        haptics.scanTick()

        capture.takePicture(
            ContextCompat.getMainExecutor(context),
            object : ImageCapture.OnImageCapturedCallback() {
                override fun onCaptureSuccess(image: ImageProxy) {
                    // Read the rotation before closing: ImageInfo is not
                    // guaranteed to be readable after the proxy is released.
                    val rotation = image.imageInfo.rotationDegrees
                    val bitmap = try {
                        image.toSafeBitmap()
                    } catch (error: Throwable) {
                        android.util.Log.e("DocumentScreen", "frame decode failed", error)
                        busy = false
                        captureButton.isEnabled = true
                        status.text = context.getString(R.string.error_generic)
                        haptics.error()
                        speech.speak(context.getString(R.string.error_generic))
                        return
                    } finally {
                        image.close()
                    }
                    process(bitmap, rotation)
                }

                override fun onError(exception: ImageCaptureException) {
                    busy = false
                    captureButton.isEnabled = true
                    status.text = context.getString(R.string.error_generic)
                    haptics.error()
                    speech.speak(context.getString(R.string.error_generic))
                }
            },
        )
    }

    private fun process(bitmap: android.graphics.Bitmap, rotation: Int) {
        val upright = BitmapUtils.rotate(bitmap, rotation)
        val script = if (scriptSpinner.selectedItemPosition == 1) {
            DocumentScript.DEVANAGARI
        } else {
            DocumentScript.LATIN
        }

        lifecycleOwner.lifecycleScope.launch {
            try {
                val result = reader.recognise(upright, script)
                if (!destroyed) deliver(result)
            } catch (error: Throwable) {
                android.util.Log.e("DocumentScreen", "OCR failed", error)
                if (!destroyed) {
                    status.text = context.getString(R.string.error_generic)
                    haptics.error()
                    speech.speak(context.getString(R.string.error_generic))
                }
            } finally {
                // The page bitmap is never needed after OCR, even on failure.
                if (upright !== bitmap) upright.recycle()
                bitmap.recycle()
                busy = false
                if (!destroyed) captureButton.isEnabled = true
            }
        }
    }

    private fun deliver(result: DocumentResult) {
        if (result.text.isBlank()) {
            lastText = ""
            status.text = context.getString(R.string.document_status_no_text)
            output.text = context.getString(R.string.document_result_placeholder)
            haptics.uncertain()
            speech.speak(context.getString(R.string.document_status_no_text))
            return
        }

        lastText = result.text
        status.text = context.getString(R.string.document_status_lines, result.lineCount)
        output.text = result.text
        output.contentDescription = result.text
        haptics.result()

        if (result.qualityWarning) {
            speech.speak(context.getString(R.string.document_quality_warning))
        }
        speech.speak(result.text, flush = false)
    }

    private fun share() {
        if (lastText.isBlank()) {
            speech.speak(context.getString(R.string.document_status_no_text))
            return
        }
        val intent = Intent(Intent.ACTION_SEND).apply {
            type = "text/plain"
            putExtra(Intent.EXTRA_TEXT, lastText)
        }
        runCatching {
            context.startActivity(
                Intent.createChooser(intent, context.getString(R.string.document_share_chooser))
            )
        }.onFailure {
            status.text = context.getString(R.string.error_generic)
            haptics.error()
            speech.speak(context.getString(R.string.error_generic))
        }
    }
}
