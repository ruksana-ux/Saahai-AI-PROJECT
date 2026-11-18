# Keep the TFLite interpreter and ML Kit entry points.
-keep class org.tensorflow.lite.** { *; }
-keep class com.google.mlkit.** { *; }
-dontwarn org.tensorflow.lite.**

# Kotlin data classes used with org.json parsing keep their names.
-keepclassmembers class org.sahaayadrishti.app.schemes.** { *; }
