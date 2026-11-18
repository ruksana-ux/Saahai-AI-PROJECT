package org.sahaayadrishti.app.settings

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.provider.Settings
import android.view.LayoutInflater
import android.view.View
import android.widget.AdapterView
import android.widget.Button
import android.widget.SeekBar
import android.widget.Spinner
import android.widget.Switch
import android.widget.TextView
import org.sahaayadrishti.app.BuildConfig
import org.sahaayadrishti.app.R
import org.sahaayadrishti.app.currency.CurrencyClassifier
import org.sahaayadrishti.app.haptics.HapticEngine
import org.sahaayadrishti.app.speech.SpeechEngine

/**
 * Settings tab.
 *
 * Everything here is local. Telemetry has its own switch, defaults to off, and
 * is never bundled with another permission or toggle.
 */
class SettingsScreen(
    private val context: Context,
    private val speech: SpeechEngine,
    private val haptics: HapticEngine,
    private val settings: SettingsStore,
) {

    val view: View = LayoutInflater.from(context).inflate(R.layout.screen_settings, null)

    private val languageTags: Array<String> =
        context.resources.getStringArray(R.array.language_tags)

    init {
        setupLanguage()
        setupRate()
        setupHaptics()
        setupTelemetry()
        setupEmergency()
        setupAbout()

        view.findViewById<Button>(R.id.btn_open_accessibility).setOnClickListener {
            val intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            runCatching { context.startActivity(intent) }
                .onFailure { speech.speak(context.getString(R.string.error_generic)) }
        }
    }

    private fun setupLanguage() {
        val spinner: Spinner = view.findViewById(R.id.settings_language)
        val saved = languageTags.indexOf(settings.languageTag).coerceAtLeast(0)
        spinner.setSelection(saved)
        spinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                val tag = languageTags[position]
                if (tag == settings.languageTag) return
                settings.languageTag = tag
                speech.languageTag = tag
                speech.speak(context.getString(R.string.settings_language))
            }

            override fun onNothingSelected(parent: AdapterView<*>?) = Unit
        }
    }

    private fun setupRate() {
        val label: TextView = view.findViewById(R.id.settings_rate_value)
        val seek: SeekBar = view.findViewById(R.id.settings_rate)
        val steps = 20
        val current = ((settings.speechRate - SettingsStore.MIN_RATE) /
            (SettingsStore.MAX_RATE - SettingsStore.MIN_RATE) * steps).toInt()
        seek.progress = current.coerceIn(0, steps)
        updateRateLabel(label, settings.speechRate)

        seek.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(bar: SeekBar?, progress: Int, fromUser: Boolean) {
                val rate = SettingsStore.MIN_RATE +
                    (SettingsStore.MAX_RATE - SettingsStore.MIN_RATE) * progress / steps
                settings.speechRate = rate
                speech.rate = rate
                updateRateLabel(label, rate)
            }

            override fun onStartTrackingTouch(bar: SeekBar?) = Unit

            override fun onStopTrackingTouch(bar: SeekBar?) {
                speech.speak(context.getString(R.string.settings_speech_rate))
            }
        })
    }

    private fun updateRateLabel(label: TextView, rate: Float) {
        label.text = context.getString(
            R.string.settings_speech_rate_summary,
            String.format(java.util.Locale.US, "%.1f", rate),
        )
    }

    private fun setupHaptics() {
        val toggle: Switch = view.findViewById(R.id.settings_haptics)
        toggle.isChecked = settings.hapticsEnabled
        haptics.enabled = settings.hapticsEnabled
        toggle.setOnCheckedChangeListener { _, checked ->
            settings.hapticsEnabled = checked
            haptics.enabled = checked
            if (checked) haptics.scanTick()
        }
    }

    private fun setupTelemetry() {
        val toggle: Switch = view.findViewById(R.id.settings_telemetry)
        toggle.isChecked = settings.telemetryOptIn
        toggle.setOnCheckedChangeListener { _, checked ->
            settings.telemetryOptIn = checked
            speech.speak(
                context.getString(
                    if (checked) R.string.settings_telemetry_on else R.string.settings_telemetry_off
                )
            )
        }
    }

    /**
     * Opens the dialler with 112 pre-filled. ACTION_DIAL needs no CALL_PHONE
     * permission and does not place the call by itself, so a mis-tap cannot
     * dial emergency services silently.
     */
    private fun setupEmergency() {
        view.findViewById<Button>(R.id.btn_call_112).setOnClickListener {
            speech.speak(context.getString(R.string.settings_emergency_call))
            val intent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:112"))
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            runCatching { context.startActivity(intent) }
                .onFailure { speech.speak(context.getString(R.string.error_generic)) }
        }
    }

    private fun setupAbout() {
        view.findViewById<TextView>(R.id.settings_version).text =
            context.getString(R.string.settings_version, BuildConfig.VERSION_NAME)

        val modelStatus = if (CurrencyClassifier.isModelBundled(context)) {
            context.getString(R.string.model_present)
        } else {
            context.getString(R.string.model_absent)
        }
        view.findViewById<TextView>(R.id.settings_model_status).text =
            context.getString(R.string.settings_model_status, modelStatus)
    }
}
