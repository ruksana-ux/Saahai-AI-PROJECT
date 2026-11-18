package in.sahaayadrishti.app.util

import android.graphics.Bitmap
import android.graphics.Matrix
import kotlin.math.min

/** Bitmap helpers shared by the currency and document pipelines. */
object BitmapUtils {

    /** Rotate a frame into upright orientation. Returns the input when no work is needed. */
    fun rotate(bitmap: Bitmap, degrees: Int): Bitmap {
        if (degrees % 360 == 0) return bitmap
        val matrix = Matrix().apply { postRotate(degrees.toFloat()) }
        return Bitmap.createBitmap(bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true)
    }

    /**
     * Crop the centred square that matches the on-screen guide box.
     *
     * Cropping at inference time (rather than asking the user to fill the whole
     * sensor) keeps the model's input distribution close to the training crops.
     */
    fun centerCrop(bitmap: Bitmap, fraction: Float): Bitmap {
        val side = (min(bitmap.width, bitmap.height) * fraction).toInt().coerceAtLeast(1)
        val left = (bitmap.width - side) / 2
        val top = (bitmap.height - side) / 2
        return Bitmap.createBitmap(bitmap, left, top, side, side)
    }
}
