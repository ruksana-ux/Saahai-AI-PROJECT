package in.sahaayadrishti.app

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.FrameLayout
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import in.sahaayadrishti.app.currency.CurrencyScreen
import in.sahaayadrishti.app.document.DocumentScreen
import in.sahaayadrishti.app.haptics.HapticEngine
import in.sahaayadrishti.app.schemes.SchemeScreen
import in.sahaayadrishti.app.settings.SettingsScreen
import in.sahaayadrishti.app.settings.SettingsStore
import in.sahaayadrishti.app.speech.SpeechEngine

/**
 * Single-activity shell with four tabs.
 *
 * The activity owns the long-lived services (speech, haptics, settings) so a
 * tab switch does not restart the voice. Each tab owns its camera binding and
 * releases it when it is replaced.
 */
class MainActivity : AppCompatActivity() {

    private lateinit var container: FrameLayout
    private lateinit var speech: SpeechEngine
    private lateinit var haptics: HapticEngine
    private lateinit var settings: SettingsStore

    private var currencyScreen: CurrencyScreen? = null
    private var documentScreen: DocumentScreen? = null
    private var schemeScreen: SchemeScreen? = null
    private var settingsScreen: SettingsScreen? = null

    private var currentTab: Tab = Tab.CURRENCY

    private val requestCamera = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (!granted) {
            speech.speak(getString(R.string.camera_permission_denied))
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        container = findViewById(R.id.screen_container)
        speech = SpeechEngine(this)
        haptics = HapticEngine(this)
        settings = SettingsStore(this)

        speech.onLanguageFallback = { requested, used ->
            speech.speak(getString(R.string.settings_language_fallback, requested, used))
        }
        speech.languageTag = settings.languageTag
        speech.rate = settings.speechRate
        haptics.enabled = settings.hapticsEnabled

        findViewById<Button>(R.id.btn_nav_money).setOnClickListener { show(Tab.CURRENCY) }
        findViewById<Button>(R.id.btn_nav_document).setOnClickListener { show(Tab.DOCUMENT) }
        findViewById<Button>(R.id.btn_nav_schemes).setOnClickListener { show(Tab.SCHEMES) }
        findViewById<Button>(R.id.btn_nav_settings).setOnClickListener { show(Tab.SETTINGS) }

        show(Tab.CURRENCY, announce = false)

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) !=
            PackageManager.PERMISSION_GRANTED
        ) {
            requestCamera.launch(Manifest.permission.CAMERA)
        }
    }

    override fun onPause() {
        super.onPause()
        currencyScreen?.onPause()
        speech.stop()
    }

    override fun onDestroy() {
        super.onDestroy()
        currencyScreen?.onDestroy()
        documentScreen?.onDestroy()
        speech.shutdown()
    }

    private fun show(tab: Tab, announce: Boolean = true) {
        if (tab == currentTab && container.childCount > 0) {
            if (announce) speech.speak(titleFor(tab))
            return
        }
        currentTab = tab

        // A document read or a scheme answer can still be speaking. Cut it off
        // so the new tab's announcement is not buried under stale text.
        speech.stop()

        currencyScreen?.onPause()
        currencyScreen?.onDestroy()
        currencyScreen = null

        documentScreen?.onDestroy()
        documentScreen = null

        schemeScreen = null
        settingsScreen = null

        container.removeAllViews()
        val screen: View = when (tab) {
            Tab.CURRENCY -> CurrencyScreen(this, this, speech, haptics)
                .also { currencyScreen = it }
                .view
            Tab.DOCUMENT -> DocumentScreen(this, this, speech, haptics, settings)
                .also { documentScreen = it }
                .view
            Tab.SCHEMES -> SchemeScreen(this, speech, haptics)
                .also { schemeScreen = it }
                .view
            Tab.SETTINGS -> SettingsScreen(this, speech, haptics, settings)
                .also { settingsScreen = it }
                .view
        }
        container.addView(screen)
        if (announce) speech.speak(titleFor(tab))
    }

    private fun titleFor(tab: Tab): String = when (tab) {
        Tab.CURRENCY -> getString(R.string.nav_money)
        Tab.DOCUMENT -> getString(R.string.nav_document)
        Tab.SCHEMES -> getString(R.string.nav_schemes)
        Tab.SETTINGS -> getString(R.string.nav_settings)
    }

    private enum class Tab { CURRENCY, DOCUMENT, SCHEMES, SETTINGS }
}
