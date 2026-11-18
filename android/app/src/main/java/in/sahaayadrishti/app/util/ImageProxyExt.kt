package in.sahaayadrishti.app.util

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.PixelFormat
import androidx.camera.core.ImageProxy

/**
 * Convert a CameraX [ImageProxy] to a [Bitmap] without relying on version-
 * specific extension functions.
 *
 * Handles both formats this app requests:
 *  - RGBA_8888 from [androidx.camera.core.ImageAnalysis]
 *  - JPEG from [androidx.camera.core.ImageCapture] (the default)
 *
 * Row padding is trimmed, otherwise the image arrives skewed on devices whose
 * row stride is not exactly `width * 4`.
 */
fun ImageProxy.toSafeBitmap(): Bitmap {
    return if (format == PixelFormat.RGBA_8888) {
        val plane = planes[0]
        val buffer = plane.buffer
        buffer.rewind()
        val pixelStride = plane.pixelStride
        val rowStride = plane.rowStride
        val rowPadding = rowStride - pixelStride * width
        val paddedWidth = width + rowPadding / pixelStride

        val padded = Bitmap.createBitmap(paddedWidth, height, Bitmap.Config.ARGB_8888)
        padded.copyPixelsFromBuffer(buffer)
        if (paddedWidth == width) {
            padded
        } else {
            val trimmed = Bitmap.createBitmap(padded, 0, 0, width, height)
            padded.recycle()
            trimmed
        }
    } else {
        val buffer = planes[0].buffer
        buffer.rewind()
        val bytes = ByteArray(buffer.remaining())
        buffer.get(bytes)
        BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
            ?: throw IllegalStateException("Could not decode the captured frame.")
    }
}
