package org.sahaayadrishti.app.currency

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class CurrencyGateTest {

    private fun prediction(
        label: String,
        confidence: Float,
        runnerUp: String? = null,
        runnerUpConfidence: Float = 0f,
    ) = CurrencyPrediction(
        label = label,
        confidence = confidence,
        runnerUpLabel = runnerUp,
        runnerUpConfidence = runnerUpConfidence,
        margin = confidence - runnerUpConfidence,
    )

    @Test
    fun `confident single answer is identified`() {
        val decision = CurrencyGate.decide(prediction("500", 0.95f, "200", 0.02f))
        assertTrue(decision is CurrencyDecision.Identified)
        assertEquals("500", (decision as CurrencyDecision.Identified).spec.key)
    }

    @Test
    fun `low confidence is uncertain, never identified`() {
        val decision = CurrencyGate.decide(prediction("500", 0.61f, "200", 0.20f))
        assertTrue(decision is CurrencyDecision.Uncertain)
    }

    @Test
    fun `small margin is uncertain even at high confidence`() {
        // 0.88 vs 0.80 is a coin flip that the confidence number hides.
        val decision = CurrencyGate.decide(prediction("100", 0.88f, "200", 0.80f))
        assertTrue(decision is CurrencyDecision.Uncertain)
    }

    @Test
    fun `unknown label is not currency`() {
        val decision = CurrencyGate.decide(prediction("unknown", 0.99f, "500", 0.005f))
        assertEquals(CurrencyDecision.NotCurrency, decision)
    }

    @Test
    fun `label outside the catalog is not currency`() {
        val decision = CurrencyGate.decide(prediction("5000", 0.99f, "500", 0.005f))
        assertEquals(CurrencyDecision.NotCurrency, decision)
    }

    @Test
    fun `non finite scores are a model error, never a denomination`() {
        val nan = Float.NaN
        val decision = CurrencyGate.decide(
            CurrencyPrediction(
                label = "500",
                confidence = nan,
                runnerUpLabel = "200",
                runnerUpConfidence = nan,
                margin = nan,
            )
        )
        assertEquals(CurrencyDecision.ModelError, decision)
    }

    @Test
    fun `thresholds are the documented values`() {
        assertEquals(0.80f, CurrencyGate.CONFIDENCE_THRESHOLD)
        assertEquals(0.15f, CurrencyGate.MARGIN_THRESHOLD)
    }
}
