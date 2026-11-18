package org.sahaayadrishti.app.currency

/**
 * Temporal smoothing for a live camera stream.
 *
 * A per-frame classifier flickers: one bad frame in five names the wrong note.
 * For a sighted user that is a cosmetic glitch; for a blind user it is a wrong
 * answer spoken with full confidence. This gate only releases a result after
 * [requiredAgreements] frames inside a short window agree, and then stays quiet
 * for [cooldownMillis] so the phone does not repeat itself.
 *
 * It deliberately does **not** smooth across different labels. A disagreement
 * resets the run, which makes the app slower but honest.
 */
class StabilityGate(
    private val requiredAgreements: Int = 3,
    private val windowSize: Int = 4,
    private val cooldownMillis: Long = 2_500,
) {

    private val recent = ArrayDeque<String>()
    private var lastEmittedLabel: String? = null
    private var lastEmittedAt = 0L

    /** Returns the label to announce, or `null` when nothing should be said. */
    fun offer(label: String, now: Long): String? {
        recent.addLast(label)
        while (recent.size > windowSize) recent.removeFirst()

        if (label == lastEmittedLabel && now - lastEmittedAt < cooldownMillis) {
            return null
        }
        if (recent.count { it == label } < requiredAgreements) {
            return null
        }
        lastEmittedLabel = label
        lastEmittedAt = now
        return label
    }

    /** A new session starts with no memory of the previous one. */
    fun reset() {
        recent.clear()
        lastEmittedLabel = null
        lastEmittedAt = 0L
    }
}
