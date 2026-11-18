package org.sahaayadrishti.app.currency

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.widget.Button
import android.widget.TextView
import androidx.camera.view.PreviewView
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.lifecycleScope
import org.sahaayadrishti.app.R
import org.sahaayadrishti.app.haptics.HapticEngine
import org.sahaayadrishti.app.speech.SpeechEngine
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * Currency tab. Speech-first, TalkBack-safe, and honest about a missing model.
 *
 * The screen never invents a denomination. If the model is absent the scan
 * button stays disabled and the tactile guide is offered instead.
 */
class CurrencyScreen(
    private val context: Context,
    private val lifecycleOwner: LifecycleOwner,
    private val speech: SpeechEngine,
    private val haptics: HapticEngine,
) {

    val view: View = LayoutInflater.from(context).inflate(R.layout.screen_currency, null)

    private val status: TextView = view.findViewById(R.id.currency_status)
    private val result: TextView = view.findViewById(R.id.currency_result)
    private val preview: PreviewView = view.findViewById(R.id.currency_preview)
    private val scanButton: Button = view.findViewById(R.id.btn_currency_scan)
    private val stopButton: Button = view.findViewById(R.id.btn_currency_stop)

    private var classifier: CurrencyClassifier? = null
    private var analyzer: CurrencyAnalyzer? = null
    private var lastSpoken: String? = null
    private var scanning = false
    private var destroyed = false

    init {
        scanButton.setOnClickListener { toggleScan() }
        view.findViewById<Button>(R.id.btn_currency_repeat).setOnClickListener {
            val text = lastSpoken
            if (text != null) {
                speech.speak(text)
            } else {
                speech.speak(context.getString(R.string.currency_result_placeholder))
            }
        }
        stopButton.setOnClickListener {
            speech.stop()
            // Stopping speech must not stop the scan or claim the scanner is
            // idle while frames are still being analysed.
            status.text = context.getString(
                if (scanning) R.string.currency_status_scanning else R.string.currency_status_ready
            )
        }

        // Loading a TFLite model reads several megabytes from the APK. Doing
        // that on the main thread freezes the app before TalkBack can speak,
        // which is exactly the wrong first impression for this audience.
        scanButton.isEnabled = false
        status.text = context.getString(R.string.currency_status_loading)

        lifecycleOwner.lifecycleScope.launch {
            val loaded = withContext(Dispatchers.IO) { CurrencyClassifier.create(context) }
            if (destroyed) {
                loaded.getOrNull()?.close()
                return@launch
            }
            val model = loaded.getOrNull()
            classifier = model
            if (model == null) {
                status.text = context.getString(R.string.currency_model_missing)
                result.text = context.getString(R.string.currency_model_missing)
                result.contentDescription = context.getString(R.string.currency_model_missing)
                scanButton.isEnabled = false
                return@launch
            }
            analyzer = CurrencyAnalyzer(
                context = context,
                classifier = model,
                onDecision = ::handleDecision,
                onModelMissing = {
                    status.text = context.getString(R.string.currency_model_missing)
                },
            )
            scanButton.isEnabled = true
            status.text = context.getString(R.string.currency_status_ready)
        }
    }

    fun onPause() {
        stopScan(announce = false)
    }

    fun onDestroy() {
        destroyed = true
        stopScan(announce = false)
        analyzer?.shutdown()
        analyzer = null
        classifier?.close()
        classifier = null
    }

    private fun toggleScan() {
        if (scanning) stopScan(announce = true) else startScan()
    }

    private fun startScan() {
        val engine = analyzer ?: return
        if (classifier == null) return
        scanning = true
        scanButton.text = context.getString(R.string.btn_stop_scan)
        status.text = context.getString(R.string.currency_status_scanning)

        engine.reset()
        engine.bind(lifecycleOwner, preview) { error ->
            scanning = false
            scanButton.text = context.getString(R.string.btn_start_scan)
            status.text = context.getString(R.string.error_generic)
            haptics.error()
            speech.speak(context.getString(R.string.error_generic))
            android.util.Log.e("CurrencyScreen", "camera error", error)
        }
        haptics.scanTick()
    }

    private fun stopScan(announce: Boolean) {
        if (!scanning) return
        scanning = false
        scanButton.text = context.getString(R.string.btn_start_scan)
        status.text = context.getString(R.string.currency_status_stopped)
        analyzer?.unbind()
        if (announce) speech.speak(context.getString(R.string.currency_status_stopped))
    }

    private fun handleDecision(decision: CurrencyDecision) {
        // A frame can finish analysing after the user has switched tabs. The
        // screen is torn down then, so speaking now would narrate an old tab.
        if (destroyed) return
        val spoken: String
        val shown: String

        when (decision) {
            CurrencyDecision.ModelUnavailable -> {
                spoken = context.getString(R.string.currency_spoken_unavailable)
                shown = spoken
                haptics.error()
            }

            CurrencyDecision.NotCurrency -> {
                spoken = context.getString(R.string.currency_spoken_not_currency)
                shown = spoken
                haptics.uncertain()
            }

            CurrencyDecision.ModelError -> {
                spoken = context.getString(R.string.currency_spoken_model_error)
                shown = spoken
                haptics.error()
            }

            is CurrencyDecision.Identified -> {
                val percent = (decision.confidence * 100).toInt().coerceIn(0, 100)
                spoken = context.getString(
                    R.string.currency_spoken_identified,
                    decision.spec.name,
                    decision.spec.tactileMark,
                )
                shown = buildString {
                    append(decision.spec.name)
                    append(". ")
                    append(context.getString(R.string.currency_confidence, percent))
                    append(" ")
                    append(decision.spec.tactileMark)
                    append("\n\n")
                    append(context.getString(R.string.currency_disclaimer))
                }
                haptics.playForCurrency(decision.spec.key)
            }

            is CurrencyDecision.Uncertain -> {
                val first = decision.top?.name
                val second = decision.runnerUp?.name
                spoken = if (first != null && second != null) {
                    context.getString(R.string.currency_spoken_uncertain, first, second)
                } else {
                    context.getString(R.string.currency_spoken_not_currency)
                }
                shown = spoken
                haptics.uncertain()
            }
        }

        lastSpoken = spoken
        result.text = shown
        result.contentDescription = shown
        status.text = context.getString(R.string.currency_status_scanning)
        speech.speak(spoken)
    }
}
