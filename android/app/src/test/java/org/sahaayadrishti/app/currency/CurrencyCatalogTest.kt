package org.sahaayadrishti.app.currency

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class CurrencyCatalogTest {

    @Test
    fun `label order matches the training labels file`() {
        // The test source set includes src/main/assets (see app/build.gradle.kts),
        // so this compares against the exact file the APK bundles.
        val fromAssets = javaClass.classLoader!!
            .getResourceAsStream("currency/labels.txt")!!
            .bufferedReader()
            .readLines()
            .filter { it.isNotBlank() }

        assertEquals(fromAssets, CurrencyCatalog.labels)
        assertEquals(13, CurrencyCatalog.labels.size)
        assertEquals(CurrencyCatalog.UNKNOWN_LABEL, CurrencyCatalog.labels.first())
    }

    @Test
    fun `every label except unknown has a spec`() {
        for (label in CurrencyCatalog.labels) {
            if (label == CurrencyCatalog.UNKNOWN_LABEL) {
                assertNull(CurrencyCatalog.spec(label))
            } else {
                assertNotNull("missing spec for $label", CurrencyCatalog.spec(label))
            }
        }
    }

    @Test
    fun `rbi bleed line counts are the verified ones`() {
        assertEquals(5, CurrencyCatalog.spec("500")!!.bleedLines)
        assertEquals(4, CurrencyCatalog.spec("200")!!.bleedLines)
        assertEquals(4, CurrencyCatalog.spec("100")!!.bleedLines)
        assertEquals(0, CurrencyCatalog.spec("50")!!.bleedLines)
        assertEquals(0, CurrencyCatalog.spec("20")!!.bleedLines)
        assertEquals(0, CurrencyCatalog.spec("10")!!.bleedLines)
        assertEquals(7, CurrencyCatalog.spec("2000")!!.bleedLines)
    }

    @Test
    fun `coins are not marked rbi verified`() {
        for (label in CurrencyCatalog.labels.filter { it.startsWith("coin_") }) {
            assertFalse(label, CurrencyCatalog.spec(label)!!.rbiVerified)
        }
    }

    @Test
    fun `haptic patterns never return empty or malformed waveforms`() {
        for (label in CurrencyCatalog.labels) {
            val pattern = CurrencyCatalog.hapticPattern(label)
            assertTrue("empty pattern for $label", pattern.isNotEmpty())
            assertEquals("pattern must start at zero for $label", 0L, pattern.first())
        }
    }

    @Test
    fun `haptic patterns are unique per denomination`() {
        val seen = mutableMapOf<String, String>()
        for (label in CurrencyCatalog.labels.filter { it != CurrencyCatalog.UNKNOWN_LABEL }) {
            val signature = CurrencyCatalog.hapticPattern(label).joinToString(",")
            val clash = seen.put(signature, label)
            assertNull("$label and $clash share a haptic pattern", clash)
        }
    }

    @Test
    fun `unmapped label still yields a fallback pattern`() {
        val pattern = CurrencyCatalog.hapticPattern("not-a-label")
        assertTrue(pattern.isNotEmpty())
        assertEquals(0L, pattern.first())
    }
}
