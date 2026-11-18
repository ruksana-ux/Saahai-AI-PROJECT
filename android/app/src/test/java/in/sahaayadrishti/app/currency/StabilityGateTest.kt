package in.sahaayadrishti.app.currency

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class StabilityGateTest {

    @Test
    fun `requires three agreeing frames before announcing`() {
        val gate = StabilityGate()
        assertNull(gate.offer("500", 0))
        assertNull(gate.offer("500", 250))
        assertEquals("500", gate.offer("500", 500))
    }

    @Test
    fun `a disagreeing frame resets the run`() {
        val gate = StabilityGate()
        assertNull(gate.offer("500", 0))
        assertNull(gate.offer("500", 250))
        assertNull(gate.offer("100", 500))
        assertNull(gate.offer("500", 750))
        assertNull(gate.offer("500", 1000))
        assertEquals("500", gate.offer("500", 1250))
    }

    @Test
    fun `same note is not repeated inside the cooldown`() {
        val gate = StabilityGate(cooldownMillis = 2_500)
        // Three agreeing frames at 0, 250 and 500 ms release the first result.
        repeat(3) { gate.offer("200", it * 250L) }
        assertNull(gate.offer("200", 750))
        assertNull(gate.offer("200", 2000))
        // Still the same label, but the cooldown has expired.
        assertEquals("200", gate.offer("200", 3_001))
    }

    @Test
    fun `a different note can be announced during the cooldown`() {
        val gate = StabilityGate(cooldownMillis = 2_500)
        repeat(3) { gate.offer("200", it * 250L) }
        assertNull(gate.offer("200", 750))
        assertNull(gate.offer("500", 1_000))
        assertNull(gate.offer("500", 1_250))
        // A different label is not blocked by the previous label's cooldown.
        assertEquals("500", gate.offer("500", 1_500))
    }

    @Test
    fun `reset clears history`() {
        val gate = StabilityGate()
        repeat(3) { gate.offer("500", it * 250L) }
        gate.reset()
        assertNull(gate.offer("500", 1000))
    }
}
