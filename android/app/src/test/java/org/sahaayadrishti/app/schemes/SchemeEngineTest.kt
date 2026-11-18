package org.sahaayadrishti.app.schemes

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test

/**
 * Runs against the real bundled `assets/schemes/schemes.json`.
 *
 * These tests are the Android counterpart of `tests/test_schemes.py`. If the
 * dataset and the two engines disagree, one of the suites fails.
 */
class SchemeEngineTest {

    private lateinit var dataset: SchemeEngine.Dataset
    private lateinit var engine: SchemeEngine

    @Before
    fun setUp() {
        val text = javaClass.classLoader!!
            .getResourceAsStream("schemes/schemes.json")!!
            .bufferedReader()
            .use { it.readText() }
        dataset = SchemeEngine.parse(text)
        engine = SchemeEngine(dataset)
    }

    @Test
    fun `bundled dataset loads and is versioned`() {
        assertEquals(4, dataset.schemes.size)
        assertTrue(dataset.version.isNotBlank())
        assertEquals("2026-11-18", dataset.lastVerified)
    }

    @Test
    fun `every record has an official source and a review date`() {
        for (scheme in dataset.schemes) {
            assertTrue(scheme.id, scheme.sourceUrl.startsWith("http"))
            assertTrue(scheme.id, scheme.lastVerified.matches(Regex("\\d{4}-\\d{2}-\\d{2}")))
            assertTrue(scheme.id, scheme.reviewDue.matches(Regex("\\d{4}-\\d{2}-\\d{2}")))
        }
    }

    @Test
    fun `adip is retrieved by name and by alias`() {
        assertEquals("adip", engine.search("ADIP income limit").first().first.id)
        assertEquals("adip", engine.search("aids and appliances scheme").first().first.id)
        assertEquals("udid", engine.search("swavlamban card").first().first.id)
        assertEquals("rpwd-act-2016", engine.search("4 percent reservation").first().first.id)
    }

    @Test
    fun `generic query is refused instead of matching everything`() {
        val answer = engine.answer("Is there a free helicopter scheme?")
        assertFalse(answer.found)
        assertTrue(answer.citations.isEmpty())
        assertTrue(answer.spokenText.contains("will not guess"))
    }

    @Test
    fun `off-topic query is refused`() {
        assertFalse(engine.answer("What is the capital of Finland?").found)
    }

    @Test
    fun `answer always carries a citation`() {
        val answer = engine.answer("How do I apply for a UDID card?")
        assertTrue(answer.found)
        assertTrue(answer.citations.isNotEmpty())
        assertTrue(answer.citations.first().sourceUrl.startsWith("http"))
        assertTrue(answer.displayText.contains("Last verified"))
    }

    @Test
    fun `income slab boundaries are inclusive at the top of each slab`() {
        val adip = dataset.schemes.first { it.id == "adip" }

        val atCeiling = engine.evaluate(
            adip,
            EligibilityProfile(
                disabilityPercent = 40.0,
                monthlyIncomeInr = 22_500.0,
                hasUdid = true,
                hasAadhaar = true,
            ),
        )
        assertEquals("eligible", atCeiling.status)
        assertEquals(100.0, atCeiling.subsidyPercent!!, 0.001)

        val above = engine.evaluate(
            adip,
            EligibilityProfile(
                disabilityPercent = 40.0,
                monthlyIncomeInr = 22_501.0,
                hasUdid = true,
                hasAadhaar = true,
            ),
        )
        assertEquals("eligible", above.status)
        assertEquals(50.0, above.subsidyPercent!!, 0.001)

        val outOfRange = engine.evaluate(
            adip,
            EligibilityProfile(
                disabilityPercent = 40.0,
                monthlyIncomeInr = 30_001.0,
                hasUdid = true,
                hasAadhaar = true,
            ),
        )
        assertEquals("not_eligible", outOfRange.status)
    }

    @Test
    fun `disability below forty percent fails adip`() {
        val adip = dataset.schemes.first { it.id == "adip" }
        val result = engine.evaluate(
            adip,
            EligibilityProfile(
                disabilityPercent = 39.0,
                monthlyIncomeInr = 10_000.0,
                hasUdid = true,
                hasAadhaar = true,
            ),
        )
        assertEquals("not_eligible", result.status)
    }

    @Test
    fun `missing facts produce unknown, not a guess`() {
        val adip = dataset.schemes.first { it.id == "adip" }
        val result = engine.evaluate(adip, EligibilityProfile())
        assertEquals("unknown", result.status)
        assertTrue(result.reasons.isNotEmpty())
    }

    @Test
    fun `tokenizer keeps denominations and drops filler`() {
        val tokens = SchemeEngine.tokenize("Is the ₹500 note covered, or 20 rupees?")
        assertTrue(tokens.contains("500"))
        assertTrue(tokens.contains("20"))
        assertFalse(tokens.contains("the"))
        assertFalse(tokens.contains("is"))
    }
}
