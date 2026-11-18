package in.sahaayadrishti.app.speech

import android.content.Context
import android.media.AudioAttributes
import android.speech.tts.TextToSpeech
import java.util.Locale

/**
 * On-device speech. Never calls a network service.
 *
 * Answers are split at sentence boundaries instead of being cut at a fixed
 * character count, because a blind user cannot re-read a truncated sentence.
 * If the requested voice is not installed, [onLanguageFallback] fires so the
 * UI can say which language is actually being spoken.
 */
class SpeechEngine(context: Context) {

    private var tts: TextToSpeech? = null
    private var ready = false
    private val pending = ArrayDeque<String>()
    private var utteranceCounter = 0

    var languageTag: String = "en-IN"
        set(value) {
            field = value
            applyLanguage()
        }

    var rate: Float = 1.0f
        set(value) {
            field = value.coerceIn(0.5f, 2.0f)
            tts?.setSpeechRate(field)
        }

    /** The locale the engine actually accepted, which may differ from the request. */
    var resolvedLanguageTag: String = "en-IN"
        private set

    var onLanguageFallback: ((requested: String, used: String) -> Unit)? = null
        set(value) {
            field = value
            // The engine may have fallen back during init, before the UI had a
            // chance to subscribe. Deliver that notice as soon as it does.
            pendingFallback?.let { (requested, used) ->
                pendingFallback = null
                value?.invoke(requested, used)
            }
        }

    private var pendingFallback: Pair<String, String>? = null

    init {
        tts = TextToSpeech(context.applicationContext) { status ->
            ready = status == TextToSpeech.SUCCESS
            if (!ready) return@TextToSpeech
            tts?.setAudioAttributes(
                AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_ASSISTANCE_ACCESSIBILITY)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                    .build()
            )
            applyLanguage()
            tts?.setSpeechRate(rate)
            flushPending()
        }
    }

    val isReady: Boolean get() = ready

    fun speak(text: String, flush: Boolean = true) {
        val clean = text.trim()
        if (clean.isEmpty()) return

        if (!ready) {
            pending.addLast(clean)
            return
        }
        val engine = tts ?: return
        if (flush) engine.stop()
        for (chunk in chunk(clean)) {
            val id = "sahaaya-${utteranceCounter++}"
            engine.speak(chunk, TextToSpeech.QUEUE_ADD, null, id)
        }
    }

    fun stop() {
        pending.clear()
        tts?.stop()
    }

    fun shutdown() {
        pending.clear()
        ready = false
        tts?.stop()
        tts?.shutdown()
        tts = null
    }

    private fun flushPending() {
        while (pending.isNotEmpty()) {
            speak(pending.removeFirst(), flush = false)
        }
    }

    private fun applyLanguage() {
        val engine = tts ?: return
        val requested = languageTag
        val primary = Locale.forLanguageTag(requested)
        val candidates = listOf(
            primary,
            Locale.Builder().setLanguage("en").setRegion("IN").build(),
            Locale.US,
        )
        for (candidate in candidates) {
            val availability = engine.setLanguage(candidate)
            val available = availability == TextToSpeech.LANG_AVAILABLE ||
                availability == TextToSpeech.LANG_COUNTRY_AVAILABLE ||
                availability == TextToSpeech.LANG_COUNTRY_VAR_AVAILABLE
            if (available) {
                resolvedLanguageTag = candidate.toLanguageTag()
                if (candidate != primary) {
                    val used = resolvedLanguageTag
                    val callback = onLanguageFallback
                    if (callback != null) {
                        callback(requested, used)
                    } else {
                        pendingFallback = requested to used
                    }
                }
                return
            }
        }
        resolvedLanguageTag = "en-US"
    }

    private fun chunk(text: String): List<String> {
        val normalised = text.replace(Regex("\\s+"), " ").trim()
        if (normalised.length <= MAX_CHARS) return listOf(normalised)

        val sentences = normalised.split(Regex("(?<=[.!?।])\\s+"))
        val chunks = mutableListOf<String>()
        var current = StringBuilder()

        for (sentence in sentences) {
            if (sentence.isEmpty()) continue
            if (current.length + sentence.length + 1 <= MAX_CHARS) {
                if (current.isNotEmpty()) current.append(' ')
                current.append(sentence)
                continue
            }
            if (current.isNotEmpty()) {
                chunks.add(current.toString())
                current = StringBuilder()
            }
            var rest = sentence
            while (rest.length > MAX_CHARS) {
                // Split at the last word boundary so a very long sentence is
                // never cut mid-word. The next chunk starts the new line.
                val cut = rest.lastIndexOf(' ', startIndex = MAX_CHARS).let {
                    if (it > 0) it else MAX_CHARS
                }
                chunks.add(rest.substring(0, cut).trim())
                rest = rest.substring(cut).trimStart()
            }
            current.append(rest)
        }
        if (current.isNotEmpty()) chunks.add(current.toString())
        return chunks
    }

    companion object {
        private const val MAX_CHARS = 180
    }
}
