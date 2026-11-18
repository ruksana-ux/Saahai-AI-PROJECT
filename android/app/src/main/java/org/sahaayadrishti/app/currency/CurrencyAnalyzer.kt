package org.sahaayadrishti.app.currency

import android.content.Context
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import android.util.Log
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import androidx.camera.core.CameraSelector
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import org.sahaayadrishti.app.util.BitmapUtils
import org.sahaayadrishti.app.util.toSafeBitmap
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicBoolean

/**
 * CameraX analysis loop for the currency screen.
 *
 * Runs at most [MIN_FRAME_INTERVAL_MS] between inferences so a cheap phone does
 * not overheat, and drops frames while one is still being processed. Frames are
 * never written to disk.
 */
class CurrencyAnalyzer(
    private val context: Context,
    private val classifier: CurrencyClassifier?,
    private val onDecision: (CurrencyDecision) -> Unit,
    private val onModelMissing: () -> Unit,
) {

    private val executor: ExecutorService = Executors.newSingleThreadExecutor()
    private val busy = AtomicBoolean(false)
    private val gate = StabilityGate()
    private var lastRunAt = 0L

    /**
     * Inference runs on [executor], but every callback in [CurrencyScreen]
     * touches Views and the TTS queue. Those must run on the main thread, so
     * the decision is re-posted rather than delivered inline.
     */
    private val mainHandler = Handler(Looper.getMainLooper())

    fun bind(lifecycleOwner: LifecycleOwner, previewView: PreviewView, onError: (Throwable) -> Unit) {
        if (classifier == null) {
            onModelMissing()
            return
        }
        val providerFuture = ProcessCameraProvider.getInstance(context)
        providerFuture.addListener({
            try {
                val provider = providerFuture.get()
                val preview = Preview.Builder().build().also {
                    it.setSurfaceProvider(previewView.surfaceProvider)
                }
                val analysis = ImageAnalysis.Builder()
                    .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                    .setOutputImageFormat(ImageAnalysis.OUTPUT_IMAGE_FORMAT_RGBA_8888)
                    .build()
                    .also { it.setAnalyzer(executor, ::analyze) }

                provider.unbindAll()
                provider.bindToLifecycle(
                    lifecycleOwner,
                    CameraSelector.DEFAULT_BACK_CAMERA,
                    preview,
                    analysis,
                )
            } catch (error: Throwable) {
                Log.e(TAG, "camera bind failed", error)
                onError(error)
            }
        }, ContextCompat.getMainExecutor(context))
    }

    fun reset() = gate.reset()

    /** Unbind the camera so a stopped scan stops using battery and the sensor. */
    fun unbind() {
        val future = ProcessCameraProvider.getInstance(context)
        if (future.isDone) {
            runCatching { future.get().unbindAll() }
        }
        gate.reset()
    }

    fun shutdown() {
        unbind()
        executor.shutdown()
    }

    private fun analyze(image: ImageProxy) {
        val now = SystemClock.elapsedRealtime()
        if (busy.get() || now - lastRunAt < MIN_FRAME_INTERVAL_MS) {
            image.close()
            return
        }
        busy.set(true)
        lastRunAt = now
        try {
            val model = classifier ?: return
            val raw = image.toSafeBitmap()
            val upright = BitmapUtils.rotate(raw, image.imageInfo.rotationDegrees)
            val cropped = BitmapUtils.centerCrop(upright, GUIDE_FRACTION)

            val prediction = model.predict(cropped)
            if (cropped !== upright) cropped.recycle()
            if (upright !== raw) upright.recycle()
            raw.recycle()

            if (prediction == null) return
            val decision = model.decisionFor(prediction)

            val label = when (decision) {
                is CurrencyDecision.Identified -> decision.spec.key
                is CurrencyDecision.Uncertain -> decision.top?.key ?: CurrencyCatalog.UNKNOWN_LABEL
                CurrencyDecision.NotCurrency -> CurrencyCatalog.UNKNOWN_LABEL
                CurrencyDecision.ModelUnavailable -> CurrencyCatalog.UNKNOWN_LABEL
                // Distinct from "unknown" so a broken frame cannot be smoothed
                // together with a legitimate "not currency" result.
                CurrencyDecision.ModelError -> MODEL_ERROR_LABEL
            }
            val stable = gate.offer(label, now)
            if (stable != null) {
                mainHandler.post { onDecision(decision) }
            }
        } catch (error: Throwable) {
            Log.e(TAG, "analysis failed", error)
        } finally {
            busy.set(false)
            image.close()
        }
    }

    companion object {
        private const val TAG = "CurrencyAnalyzer"

        /** ~4 frames per second. Enough for a hand-held scan, gentle on battery. */
        private const val MIN_FRAME_INTERVAL_MS = 250L

        /** Matches the guide box inset in `screen_currency.xml` (28dp on each side). */
        private const val GUIDE_FRACTION = 0.82f

        /** Internal label for a broken inference; never shown to the user. */
        private const val MODEL_ERROR_LABEL = "__model_error__"
    }
}
