package in.sahaayadrishti.app.document

import android.graphics.Bitmap
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.Text
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.TextRecognizer
import com.google.mlkit.vision.text.devanagari.DevanagariTextRecognizerOptions
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import kotlin.math.abs
import kotlin.math.sqrt
import kotlinx.coroutines.suspendCancellableCoroutine

enum class DocumentScript { LATIN, DEVANAGARI }

data class DocumentResult(
    val text: String,
    val lineCount: Int,
    val qualityWarning: Boolean,
    val script: DocumentScript,
)

/**
 * Offline OCR over a single captured page.
 *
 * Uses ML Kit's **bundled** recognisers (`text-recognition` and
 * `text-recognition-devanagari`), which ship in the APK and work with no
 * network. The play-services variants are deliberately not used: they download
 * the model on first run, which fails exactly where this app is meant to work.
 *
 * A blur/contrast gate runs before OCR. It does not reject the page, because a
 * blind user cannot easily re-shoot; it sets [DocumentResult.qualityWarning] so
 * the result is announced as possibly wrong.
 */
class DocumentReader {

    private var latin: TextRecognizer? = null
    private var devanagari: TextRecognizer? = null

    suspend fun recognise(bitmap: Bitmap, script: DocumentScript): DocumentResult {
        val recogniser = when (script) {
            DocumentScript.LATIN -> latin ?: TextRecognition
                .getClient(TextRecognizerOptions.Builder().build())
                .also { latin = it }
            DocumentScript.DEVANAGARI -> devanagari ?: TextRecognition
                .getClient(DevanagariTextRecognizerOptions.Builder().build())
                .also { devanagari = it }
        }
        val image = InputImage.fromBitmap(bitmap, 0)
        val recognised = suspendCancellableCoroutine<Text> { continuation ->
            recogniser.process(image)
                .addOnSuccessListener { continuation.resume(it) }
                .addOnFailureListener { continuation.resumeWithException(it) }
        }

        val lines = readingOrder(recognised)
        val body = lines.joinToString("\n") { it.text.trim() }.trim()
        val warning = body.isEmpty() || isLowQuality(bitmap)

        return DocumentResult(
            text = body,
            lineCount = lines.size,
            qualityWarning = warning,
            script = script,
        )
    }

    fun close() {
        latin?.close()
        devanagari?.close()
        latin = null
        devanagari = null
    }

    private companion object {
        /**
         * Lines whose top edges differ by less than this are treated as the
         * same visual row. 8px at ~1080p is well under a line height.
         */
        const val ROW_TOLERANCE_PX = 8
    }

    /**
     * Sort lines top-to-bottom, then left-to-right, with a small vertical
     * tolerance so two lines on the same visual row are not interleaved by a
     * one-pixel skew. ML Kit's block order is good but not guaranteed across
     * columns.
     */
    private fun readingOrder(text: Text): List<Text.Line> {
        val lines = mutableListOf<Text.Line>()
        for (block in text.textBlocks) {
            lines.addAll(block.lines)
        }
        return lines.sortedWith(
            compareBy<Text.Line> { (it.boundingBox?.top ?: 0) / ROW_TOLERANCE_PX }
                .thenBy { it.boundingBox?.left ?: 0 }
        )
    }

    /**
     * Laplacian variance on a downscaled grayscale copy.
     *
     * This is the standard cheap focus measure. A flat, washed-out page and a
     * blurred page both score low, which is what we want to flag. The threshold
     * is conservative because a false warning is annoying but a silent wrong
     * reading is dangerous.
     */
    private fun isLowQuality(bitmap: Bitmap): Boolean {
        val width = 160
        val height = (bitmap.height.toFloat() / bitmap.width * width).toInt().coerceAtLeast(1)
        val small = Bitmap.createScaledBitmap(bitmap, width, height, true)
        val pixels = IntArray(width * height)
        small.getPixels(pixels, 0, width, 0, 0, width, height)
        if (small !== bitmap) small.recycle()

        val gray = IntArray(pixels.size) { index ->
            val pixel = pixels[index]
            val r = (pixel shr 16) and 0xFF
            val g = (pixel shr 8) and 0xFF
            val b = pixel and 0xFF
            (r * 299 + g * 587 + b * 114) / 1000
        }

        var sum = 0.0
        var sumSquares = 0.0
        var count = 0
        var laplacianSum = 0.0
        var laplacianSquares = 0.0

        for (y in 1 until height - 1) {
            for (x in 1 until width - 1) {
                val index = y * width + x
                val centre = gray[index].toDouble()
                sum += centre
                sumSquares += centre * centre
                count++

                val laplacian = (
                    -4 * centre +
                        gray[index - 1] + gray[index + 1] +
                        gray[index - width] + gray[index + width]
                    )
                laplacianSum += laplacian
                laplacianSquares += laplacian * laplacian
            }
        }
        if (count == 0) return true

        val mean = sum / count
        val variance = (sumSquares / count) - mean * mean
        val laplacianMean = laplacianSum / count
        val laplacianVariance = (laplacianSquares / count) - laplacianMean * laplacianMean

        val tooDark = mean < 45
        val tooBright = mean > 235
        val tooFlat = sqrt(abs(variance)) < 12.0
        val tooBlurry = laplacianVariance < 90.0
        return tooDark || tooBright || tooFlat || tooBlurry
    }
}
