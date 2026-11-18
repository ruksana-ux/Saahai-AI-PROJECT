package in.sahaayadrishti.app.schemes

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.widget.Button
import android.widget.CheckBox
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import in.sahaayadrishti.app.R
import in.sahaayadrishti.app.haptics.HapticEngine
import in.sahaayadrishti.app.speech.SpeechEngine

/**
 * Scheme navigator tab.
 *
 * The answer text is produced by [SchemeEngine] from the bundled dataset and
 * always ends with the official source and the date it was checked. Speech is
 * the primary channel; the on-screen text exists for sighted helpers and for
 * users with partial vision.
 */
class SchemeScreen(
    private val context: Context,
    private val speech: SpeechEngine,
    private val haptics: HapticEngine,
) {

    val view: View = LayoutInflater.from(context).inflate(R.layout.screen_schemes, null)

    private val query: EditText = view.findViewById(R.id.scheme_query)
    private val result: TextView = view.findViewById(R.id.scheme_result)
    private val datasetStatus: TextView = view.findViewById(R.id.scheme_dataset_status)
    private val profileContainer: LinearLayout = view.findViewById(R.id.profile_container)
    private val disability: EditText = view.findViewById(R.id.profile_disability)
    private val income: EditText = view.findViewById(R.id.profile_income)
    private val hasUdid: CheckBox = view.findViewById(R.id.profile_has_udid)
    private val hasAadhaar: CheckBox = view.findViewById(R.id.profile_has_aadhaar)

    private var engine: SchemeEngine? = null
    private var lastSpoken: String? = null

    init {
        val loaded = runCatching { SchemeEngine.load(context) }
        loaded.onSuccess { dataset ->
            engine = SchemeEngine(dataset)
            datasetStatus.text = context.getString(
                R.string.scheme_dataset_status,
                dataset.version,
                dataset.schemes.size,
                dataset.lastVerified,
            )
        }.onFailure { error ->
            android.util.Log.e("SchemeScreen", "dataset load failed", error)
            datasetStatus.text = context.getString(R.string.scheme_dataset_error)
        }

        view.findViewById<CheckBox>(R.id.check_use_profile).setOnCheckedChangeListener { _, checked ->
            profileContainer.visibility = if (checked) View.VISIBLE else View.GONE
        }

        view.findViewById<Button>(R.id.btn_preset_adip).setOnClickListener {
            query.setText("ADIP income limit and documents")
            runSearch()
        }
        view.findViewById<Button>(R.id.btn_preset_udid).setOnClickListener {
            query.setText("How do I apply for a UDID card")
            runSearch()
        }
        view.findViewById<Button>(R.id.btn_preset_rpwd).setOnClickListener {
            query.setText("RPwD Act reservation in government jobs")
            runSearch()
        }

        view.findViewById<Button>(R.id.btn_scheme_search).setOnClickListener { runSearch() }
        view.findViewById<Button>(R.id.btn_scheme_speak).setOnClickListener {
            val text = lastSpoken
            if (text != null) speech.speak(text) else speech.speak(result.text.toString())
        }
        view.findViewById<Button>(R.id.btn_scheme_stop).setOnClickListener { speech.stop() }
    }

    private fun runSearch() {
        val text = query.text.toString().trim()
        if (text.isEmpty()) {
            speech.speak(context.getString(R.string.schemes_query_hint))
            return
        }

        val active = engine
        if (active == null) {
            result.text = context.getString(R.string.scheme_dataset_error)
            speech.speak(context.getString(R.string.scheme_dataset_error))
            haptics.error()
            return
        }

        val profile = if (view.findViewById<CheckBox>(R.id.check_use_profile).isChecked) {
            EligibilityProfile(
                disabilityPercent = disability.text.toString().toDoubleOrNull(),
                monthlyIncomeInr = income.text.toString().toDoubleOrNull(),
                hasUdid = hasUdid.isChecked,
                hasAadhaar = hasAadhaar.isChecked,
            )
        } else {
            null
        }

        val answer = active.answer(text, profile)
        result.text = answer.displayText
        result.contentDescription = answer.displayText
        lastSpoken = answer.spokenText
        if (answer.found) haptics.result() else haptics.uncertain()
        speech.speak(answer.spokenText)
    }
}
