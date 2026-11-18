package in.sahaayadrishti.app.haptics

import in.sahaayadrishti.app.currency.CurrencyCatalog
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * A blind user learns one waveform per denomination. If a generic cue reuses a
 * denomination waveform, "read succeeded" becomes indistinguishable from
 * "₹5 coin". These tests make that collision a build failure.
 */
class HapticPatternsTest {

    private val genericCues = mapOf(
        "scan tick" to HapticPatterns.SCAN_TICK,
        "success" to HapticPatterns.SUCCESS,
        "uncertain" to HapticPatterns.UNCERTAIN,
        "error" to HapticPatterns.ERROR,
    )

    @Test
    fun `generic cues are distinct from each other`() {
        val seen = mutableMapOf<String, String>()
        for ((name, pattern) in genericCues) {
            val clash = seen.put(pattern.joinToString(","), name)
            assertNull("$name and $clash share a waveform", clash)
        }
    }

    @Test
    fun `no generic cue collides with a denomination`() {
        val denominations = CurrencyCatalog.labels
            .filter { it != CurrencyCatalog.UNKNOWN_LABEL }
            .associateWith { CurrencyCatalog.hapticPattern(it).joinToString(",") }

        for ((name, pattern) in genericCues) {
            val signature = pattern.joinToString(",")
            for ((label, denomination) in denominations) {
                assertTrue(
                    "$name waveform equals the $label waveform",
                    signature != denomination,
                )
            }
        }
    }

    @Test
    fun `every cue is well formed`() {
        for ((name, pattern) in genericCues) {
            assertTrue("$name is empty", pattern.isNotEmpty())
            assertTrue("$name has an odd length", pattern.size % 2 == 0)
            assertTrue("$name must start at zero delay", pattern.first() == 0L)
            assertTrue("$name has a non-positive pulse", pattern.drop(1).all { it > 0 })
        }
    }
}
