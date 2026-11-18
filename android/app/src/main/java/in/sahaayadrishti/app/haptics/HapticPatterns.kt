package in.sahaayadrishti.app.haptics

/**
 * Non-currency haptic cues, kept as pure data so a JVM test can prove they do
 * not collide with any denomination waveform in
 * [in.sahaayadrishti.app.currency.CurrencyCatalog].
 *
 * Android's waveform format is `[delay, on, off, on, off, ...]` in
 * milliseconds. Every pattern starts with a zero delay so it begins the moment
 * it is played.
 */
object HapticPatterns {

    /** A short tick: the app has started listening or scanning. */
    val SCAN_TICK: LongArray = longArrayOf(0, 40)

    /**
     * Generic success cue for the document and scheme screens. Three short
     * pulses; deliberately unlike the single-pulse ₹10 note and the
     * long-pulse notes.
     */
    val SUCCESS: LongArray = longArrayOf(0, 80, 50, 80, 50, 80)

    /** "I am not sure": two long pulses, clearly heavier than a success cue. */
    val UNCERTAIN: LongArray = longArrayOf(0, 250, 80, 250)

    /** Hard failure: three long pulses. The heaviest cue in the app. */
    val ERROR: LongArray = longArrayOf(0, 400, 100, 400, 100, 400)
}
