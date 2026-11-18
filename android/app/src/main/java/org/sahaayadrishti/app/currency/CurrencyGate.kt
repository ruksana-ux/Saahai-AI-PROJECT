package org.sahaayadrishti.app.currency

/**
 * The decision gate, isolated from TensorFlow so it can be unit-tested on the
 * JVM and reviewed as plain logic.
 *
 * Two numbers matter:
 *  - [CONFIDENCE_THRESHOLD]: below this the app must not name a denomination.
 *  - [MARGIN_THRESHOLD]: if the top two are close, naming one is a coin flip.
 *
 * Both are deliberately conservative. Missing a note costs a second scan;
 * naming the wrong note can make a user hand over the wrong change.
 */
object CurrencyGate {

    const val CONFIDENCE_THRESHOLD = 0.80f
    const val MARGIN_THRESHOLD = 0.15f

    fun decide(prediction: CurrencyPrediction): CurrencyDecision {
        // Guard first: NaN/Infinity would slip through every `<` comparison.
        if (!prediction.confidence.isFinite() || !prediction.margin.isFinite()) {
            return CurrencyDecision.ModelError
        }
        if (prediction.label == CurrencyCatalog.UNKNOWN_LABEL) {
            return CurrencyDecision.NotCurrency
        }
        val top = CurrencyCatalog.spec(prediction.label)
            ?: return CurrencyDecision.NotCurrency
        val runnerUp = CurrencyCatalog.spec(prediction.runnerUpLabel ?: "")

        if (prediction.confidence < CONFIDENCE_THRESHOLD || prediction.margin < MARGIN_THRESHOLD) {
            return CurrencyDecision.Uncertain(top, runnerUp, prediction.confidence)
        }
        return CurrencyDecision.Identified(top, prediction.confidence)
    }
}
