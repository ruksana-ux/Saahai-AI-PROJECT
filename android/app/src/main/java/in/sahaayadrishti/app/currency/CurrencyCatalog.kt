package in.sahaayadrishti.app.currency

/**
 * Static, human-checkable facts about Indian notes and coins.
 *
 * Every tactile fact here was read from RBI's "For Visually Impaired" page
 * (https://indiancurrency.rbi.org.in/visual-impairment) on 18 November 2026.
 * If a value changes, change it here, in `currency_engine.py` and in
 * `docs/CLAIMS_MATRIX.md` together.
 *
 * Coins are marked `rbiVerified = false` on purpose: the shape and size notes
 * are widely reported but the RBI accessibility page does not publish a
 * per-coin tactile table, so the app must not present them as RBI-verified.
 */
class CurrencySpec(
    val key: String,
    val name: String,
    val kind: Kind,
    val colour: String,
    val motif: String,
    val bleedLines: Int,
    val tactileMark: String,
    val hapticPattern: LongArray,
    val rbiVerified: Boolean,
) {
    enum class Kind { NOTE, COIN }
}

object CurrencyCatalog {

    /** Order must match `ml/currency/labels.txt` and the TFLite output layer. */
    val labels: List<String> = listOf(
        "unknown",
        "10", "20", "50", "100", "200", "500", "2000",
        "coin_1", "coin_2", "coin_5", "coin_10", "coin_20",
    )

    const val UNKNOWN_LABEL = "unknown"

    private val specs: Map<String, CurrencySpec> = listOf(
        CurrencySpec(
            key = "2000",
            name = "2000 rupee note",
            kind = CurrencySpec.Kind.NOTE,
            colour = "magenta",
            motif = "Mangalyaan",
            bleedLines = 7,
            tactileMark = "7 angular bleed lines and a raised horizontal rectangle. " +
                "RBI has announced withdrawal from circulation; the note is still legal tender.",
            hapticPattern = longArrayOf(0, 180, 70, 180, 70, 180, 70, 180, 70, 180, 70, 180, 70, 180),
            rbiVerified = true,
        ),
        CurrencySpec(
            key = "500",
            name = "500 rupee note",
            kind = CurrencySpec.Kind.NOTE,
            colour = "stone grey",
            motif = "Red Fort",
            bleedLines = 5,
            tactileMark = "5 angular bleed lines in three blocks, plus a raised circle with the denomination.",
            hapticPattern = longArrayOf(0, 180, 70, 180, 70, 180, 70, 180, 70, 180),
            rbiVerified = true,
        ),
        CurrencySpec(
            key = "200",
            name = "200 rupee note",
            kind = CurrencySpec.Kind.NOTE,
            colour = "bright yellow",
            motif = "Sanchi Stupa",
            bleedLines = 4,
            tactileMark = "4 angular bleed lines with 2 circles in between, plus a raised H mark.",
            // Four long pulses, slow gap. Distinct from ₹100, which also has
            // four bleed lines but uses the fast gap.
            hapticPattern = longArrayOf(0, 180, 120, 180, 120, 180, 120, 180),
            rbiVerified = true,
        ),
        CurrencySpec(
            key = "100",
            name = "100 rupee note",
            kind = CurrencySpec.Kind.NOTE,
            colour = "lavender",
            motif = "Rani ki Vav",
            bleedLines = 4,
            tactileMark = "4 angular bleed lines, plus a raised triangle with microtext 100.",
            // Four long pulses, fast gap. See ₹200 for the slow-gap variant.
            hapticPattern = longArrayOf(0, 180, 70, 180, 70, 180, 70, 180),
            rbiVerified = true,
        ),
        CurrencySpec(
            key = "50",
            name = "50 rupee note",
            kind = CurrencySpec.Kind.NOTE,
            colour = "fluorescent blue",
            motif = "Hampi with chariot",
            bleedLines = 0,
            tactileMark = "No bleed lines. Use the raised intaglio print and the note size.",
            hapticPattern = longArrayOf(0, 180, 70, 180),
            rbiVerified = true,
        ),
        CurrencySpec(
            key = "20",
            name = "20 rupee note",
            kind = CurrencySpec.Kind.NOTE,
            colour = "greenish yellow",
            motif = "Ellora Caves",
            bleedLines = 0,
            tactileMark = "No bleed lines. Use the raised intaglio print and the note size.",
            hapticPattern = longArrayOf(0, 180),
            rbiVerified = true,
        ),
        CurrencySpec(
            key = "10",
            name = "10 rupee note",
            kind = CurrencySpec.Kind.NOTE,
            colour = "chocolate brown",
            motif = "Konark Sun Temple",
            bleedLines = 0,
            tactileMark = "No bleed lines. Use the raised intaglio print and the note size.",
            hapticPattern = longArrayOf(0, 90),
            rbiVerified = true,
        ),
        CurrencySpec(
            key = "coin_20",
            name = "20 rupee coin",
            kind = CurrencySpec.Kind.COIN,
            colour = "silver",
            motif = "12-sided",
            bleedLines = 0,
            tactileMark = "12-sided coin. Count the straight edges with your thumb.",
            hapticPattern = longArrayOf(0, 120, 60, 120, 60, 120),
            rbiVerified = false,
        ),
        CurrencySpec(
            key = "coin_10",
            name = "10 rupee coin",
            kind = CurrencySpec.Kind.COIN,
            colour = "bimetallic",
            motif = "two-metal ring",
            bleedLines = 0,
            tactileMark = "Bimetallic: a distinct outer ring around an inner disc.",
            // Two medium pulses with a long gap: the "ring around a disc" cue.
            hapticPattern = longArrayOf(0, 120, 200, 120),
            rbiVerified = false,
        ),
        CurrencySpec(
            key = "coin_5",
            name = "5 rupee coin",
            kind = CurrencySpec.Kind.COIN,
            colour = "silver",
            motif = "round",
            bleedLines = 0,
            tactileMark = "Round and larger than the 2 rupee coin.",
            hapticPattern = longArrayOf(0, 120, 60, 120),
            rbiVerified = false,
        ),
        CurrencySpec(
            key = "coin_2",
            name = "2 rupee coin",
            kind = CurrencySpec.Kind.COIN,
            colour = "silver",
            motif = "round",
            bleedLines = 0,
            tactileMark = "Round, smaller than the 5 rupee coin.",
            hapticPattern = longArrayOf(0, 120),
            rbiVerified = false,
        ),
        CurrencySpec(
            key = "coin_1",
            name = "1 rupee coin",
            kind = CurrencySpec.Kind.COIN,
            colour = "silver",
            motif = "round",
            bleedLines = 0,
            tactileMark = "Round and the smallest of the commonly circulated coins.",
            hapticPattern = longArrayOf(0, 60),
            rbiVerified = false,
        ),
    ).associateBy { it.key }

    fun spec(key: String): CurrencySpec? = specs[key]

    /** Haptics must never crash the result path for an unmapped label. */
    fun hapticPattern(key: String): LongArray =
        specs[key]?.hapticPattern ?: longArrayOf(0, 300, 120, 300)
}
