package in.sahaayadrishti.app.haptics

import android.content.Context
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import in.sahaayadrishti.app.currency.CurrencyCatalog

/**
 * Named haptic patterns. Haptics supplement speech; they are never the only
 * channel, because a phone can be on silent or in a pocket.
 *
 * Patterns follow docs/ACCESSIBILITY.md.
 */
class HapticEngine(context: Context) {

    private val vibrator: Vibrator? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        (context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as? VibratorManager)
            ?.defaultVibrator
    } else {
        @Suppress("DEPRECATION")
        context.getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator
    }

    var enabled: Boolean = true

    fun playForCurrency(key: String) {
        play(CurrencyCatalog.hapticPattern(key))
    }

    fun play(pattern: LongArray) {
        if (!enabled) return
        val device = vibrator ?: return
        if (!device.hasVibrator()) return
        device.vibrate(VibrationEffect.createWaveform(pattern, -1))
    }

    fun scanTick() = play(HapticPatterns.SCAN_TICK)

    /**
     * Generic success cue for the document and scheme screens. Kept distinct
     * from every denomination waveform in [CurrencyCatalog] so a "read
     * succeeded" buzz can never be mistaken for "₹5 coin".
     */
    fun result() = play(HapticPatterns.SUCCESS)

    fun uncertain() = play(HapticPatterns.UNCERTAIN)

    fun error() = play(HapticPatterns.ERROR)
}
