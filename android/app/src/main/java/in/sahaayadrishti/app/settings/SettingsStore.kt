package in.sahaayadrishti.app.settings

import android.content.Context
import android.content.SharedPreferences

/**
 * Local settings. No account, no cloud sync.
 *
 * Telemetry is off until the user turns it on, and the switch is separate from
 * every other toggle so consent cannot be bundled.
 */
class SettingsStore(context: Context) {

    private val prefs: SharedPreferences =
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    var languageTag: String
        get() = prefs.getString(KEY_LANGUAGE, "en-IN") ?: "en-IN"
        set(value) {
            prefs.edit().putString(KEY_LANGUAGE, value).apply()
        }

    var speechRate: Float
        get() = prefs.getFloat(KEY_RATE, 1.0f)
        set(value) {
            prefs.edit().putFloat(KEY_RATE, value.coerceIn(MIN_RATE, MAX_RATE)).apply()
        }

    var hapticsEnabled: Boolean
        get() = prefs.getBoolean(KEY_HAPTICS, true)
        set(value) {
            prefs.edit().putBoolean(KEY_HAPTICS, value).apply()
        }

    var telemetryOptIn: Boolean
        get() = prefs.getBoolean(KEY_TELEMETRY, false)
        set(value) {
            prefs.edit().putBoolean(KEY_TELEMETRY, value).apply()
        }

    var documentScript: Int
        get() = prefs.getInt(KEY_SCRIPT, 0)
        set(value) {
            prefs.edit().putInt(KEY_SCRIPT, value).apply()
        }

    companion object {
        private const val PREFS_NAME = "sahaaya_settings"
        private const val KEY_LANGUAGE = "language_tag"
        private const val KEY_RATE = "speech_rate"
        private const val KEY_HAPTICS = "haptics"
        private const val KEY_TELEMETRY = "telemetry"
        private const val KEY_SCRIPT = "document_script"
        const val MIN_RATE = 0.5f
        const val MAX_RATE = 2.0f
    }
}
