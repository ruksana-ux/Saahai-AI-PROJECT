package org.sahaayadrishti.app.currency

import android.content.Context
import android.graphics.Bitmap
import org.json.JSONObject
import org.tensorflow.lite.Interpreter
import java.io.InputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.math.exp

/** A single calibrated prediction. */
data class CurrencyPrediction(
    val label: String,
    val confidence: Float,
    val runnerUpLabel: String?,
    val runnerUpConfidence: Float,
    val margin: Float,
)

/** What the UI should say, decided by the gate rather than by the caller. */
sealed interface CurrencyDecision {
    /** The model file is absent or unusable. Never guess a denomination. */
    data object ModelUnavailable : CurrencyDecision

    /** The model is confident enough to name one denomination. */
    data class Identified(val spec: CurrencySpec, val confidence: Float) : CurrencyDecision

    /** Two denominations are close. Naming one would be a guess. */
    data class Uncertain(val top: CurrencySpec?, val runnerUp: CurrencySpec?, val confidence: Float) :
        CurrencyDecision

    /** The model says this is not a supported note or coin. */
    data object NotCurrency : CurrencyDecision

    /**
     * The model produced a non-finite score (NaN/Infinity). That is a broken
     * inference, not a denomination, so it must never reach the gate's
     * "confident" branch.
     */
    data object ModelError : CurrencyDecision
}

/**
 * On-device currency classifier.
 *
 * Contract with the exported model (`ml/currency/export_tflite.py`):
 *  - input: float32 `[1, 224, 224, 3]`, raw 0-255 pixels, RGB
 *  - output: float32 logits over [CurrencyCatalog.labels]
 *  - `currency_model.json` carries `temperature`, `normalisation` and `labels`
 *
 * If the model or metadata is missing, [decisionFor] returns
 * [CurrencyDecision.ModelUnavailable]. There is no fallback heuristic. The old
 * prototype invented a 91-97% confidence from average pixel colour, which is
 * exactly the failure mode a blind user cannot detect.
 */
class CurrencyClassifier private constructor(
    private val interpreter: Interpreter,
    private val labels: List<String>,
    private val temperature: Float,
    private val inputSize: Int,
    private val normalisation: String,
    val modelDescription: String,
) {

    fun predict(bitmap: Bitmap): CurrencyPrediction? {
        val input = preprocess(bitmap) ?: return null
        val output = Array(1) { FloatArray(labels.size) }
        interpreter.run(input, output)
        return decode(output[0])
    }

    /** Apply the calibrated gate. Thresholds live in one place, not in the UI. */
    fun decisionFor(prediction: CurrencyPrediction): CurrencyDecision =
        CurrencyGate.decide(prediction)

    fun close() {
        interpreter.close()
    }

    private fun preprocess(bitmap: Bitmap): ByteBuffer? {
        val scaled = Bitmap.createScaledBitmap(bitmap, inputSize, inputSize, true)
        val buffer = ByteBuffer.allocateDirect(1 * inputSize * inputSize * 3 * 4)
            .order(ByteOrder.nativeOrder())
        val pixels = IntArray(inputSize * inputSize)
        scaled.getPixels(pixels, 0, inputSize, 0, 0, inputSize, inputSize)
        for (pixel in pixels) {
            val r = (pixel shr 16) and 0xFF
            val g = (pixel shr 8) and 0xFF
            val b = pixel and 0xFF
            when (normalisation) {
                // MobileNetV3 is exported with include_preprocessing=True, so the
                // graph rescales internally. Dividing again here would halve
                // accuracy and is the classic deployment bug.
                "raw_0_255" -> {
                    buffer.putFloat(r.toFloat())
                    buffer.putFloat(g.toFloat())
                    buffer.putFloat(b.toFloat())
                }
                "0_1" -> {
                    buffer.putFloat(r / 255f)
                    buffer.putFloat(g / 255f)
                    buffer.putFloat(b / 255f)
                }
                "minus1_1" -> {
                    buffer.putFloat(r / 127.5f - 1f)
                    buffer.putFloat(g / 127.5f - 1f)
                    buffer.putFloat(b / 127.5f - 1f)
                }
                else -> return null
            }
        }
        buffer.rewind()
        if (scaled !== bitmap) scaled.recycle()
        return buffer
    }

    private fun decode(logits: FloatArray): CurrencyPrediction {
        // A NaN logit poisons the softmax: every comparison against a threshold
        // is false, so the old code would have "identified" a note with NaN
        // confidence. Reject the whole frame instead.
        if (logits.isEmpty() || logits.any { !it.isFinite() }) {
            return CurrencyPrediction(
                label = CurrencyCatalog.UNKNOWN_LABEL,
                confidence = Float.NaN,
                runnerUpLabel = null,
                runnerUpConfidence = Float.NaN,
                margin = Float.NaN,
            )
        }

        val scaled = FloatArray(logits.size)
        val max = logits.maxOrNull() ?: 0f
        var total = 0f
        for (i in logits.indices) {
            scaled[i] = exp(((logits[i] - max) / temperature).toDouble()).toFloat()
            total += scaled[i]
        }
        if (total <= 0f) total = 1f

        val order = logits.indices.sortedByDescending { scaled[it] / total }
        val best = order[0]
        val second = if (order.size > 1) order[1] else best
        val bestConfidence = scaled[best] / total
        val secondConfidence = scaled[second] / total
        return CurrencyPrediction(
            label = labels[best],
            confidence = bestConfidence,
            runnerUpLabel = labels.getOrNull(second),
            runnerUpConfidence = secondConfidence,
            margin = bestConfidence - secondConfidence,
        )
    }

    companion object {
        private const val MODEL_ASSET = "currency/currency_model.tflite"
        private const val META_ASSET = "currency/currency_model.json"

        /**
         * Cheap asset-existence check for the Settings screen. It does not load
         * TFLite, so opening Settings never pays the model-load cost.
         */
        fun isModelBundled(context: Context): Boolean = try {
            context.assets.open(MODEL_ASSET).close()
            context.assets.open(META_ASSET).close()
            true
        } catch (error: Throwable) {
            false
        }

        /**
         * Load the bundled model, or return `null` with a reason. A build that
         * ships without a trained model is valid: the app says so instead of
         * pretending to classify.
         */
        fun create(context: Context): Result<CurrencyClassifier> = try {
            val assets = context.assets
            val metaText = assets.open(META_ASSET).bufferedReader().use { it.readText() }
            val meta = JSONObject(metaText)

            val labels = meta.optJSONArray("labels")?.let { array ->
                List(array.length()) { array.getString(it) }
            } ?: CurrencyCatalog.labels

            val size = meta.optJSONArray("input_size")?.let { array ->
                array.getInt(0)
            } ?: 224

            val temperature = meta.optDouble("temperature", 1.0).toFloat().coerceAtLeast(1e-3f)
            val normalisation = meta.optString("normalisation", "raw_0_255")

            val options = Interpreter.Options().apply {
                setNumThreads(2)
                setUseXNNPACK(true)
            }
            val interpreter = Interpreter(
                loadModel(assets.open(MODEL_ASSET)),
                options,
            )

            try {
                val inputShape = interpreter.getInputTensor(0).shape()
                require(inputShape.size == 4 && inputShape[1] == size && inputShape[2] == size) {
                    "Model input ${inputShape.toList()} does not match metadata size $size."
                }
                val outputClasses = interpreter.getOutputTensor(0).shape().last()
                require(outputClasses == labels.size) {
                    "Model has $outputClasses outputs but metadata lists ${labels.size} labels."
                }
            } catch (error: Throwable) {
                // Do not leak a native interpreter when the contract check fails.
                interpreter.close()
                throw error
            }

            Result.success(
                CurrencyClassifier(
                    interpreter = interpreter,
                    labels = labels,
                    temperature = temperature,
                    inputSize = size,
                    normalisation = normalisation,
                    modelDescription = meta.optString("quantisation", "unknown"),
                )
            )
        } catch (error: Throwable) {
            Result.failure(error)
        }

        private fun loadModel(stream: InputStream): ByteBuffer {
            val bytes = stream.use { it.readBytes() }
            return ByteBuffer.allocateDirect(bytes.size).order(ByteOrder.nativeOrder()).apply {
                put(bytes)
                rewind()
            }
        }
    }
}
