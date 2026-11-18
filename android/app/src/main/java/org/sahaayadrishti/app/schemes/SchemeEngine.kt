package org.sahaayadrishti.app.schemes

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.time.LocalDate
import kotlin.math.ln

/**
 * A scheme record exactly as it is stored in `assets/schemes/schemes.json`.
 *
 * The dataset is the single source of truth. It is the same file the Python
 * prototype and the backend serve, so an edit can never drift between clients.
 */
data class Scheme(
    val id: String,
    val name: String,
    val aliases: List<String>,
    val category: String,
    val summary: String,
    val benefits: List<String>,
    val documentsRequired: List<String>,
    val howToApply: List<String>,
    val eligibilityNotes: List<String>,
    val disabilityPercentMin: Double,
    val requiresUdid: Boolean,
    val requiresAadhaar: Boolean,
    val incomeSlabs: List<IncomeSlab>,
    val sourceUrl: String,
    val lastVerified: String,
    val reviewDue: String,
    val verificationStatus: String,
    val helpline: String?,
)

data class IncomeSlab(
    val minMonthlyInr: Double,
    val maxMonthlyInr: Double?,
    val subsidyPercent: Double,
)

data class EligibilityProfile(
    val disabilityPercent: Double? = null,
    val monthlyIncomeInr: Double? = null,
    val hasUdid: Boolean? = null,
    val hasAadhaar: Boolean? = null,
)

data class EligibilityResult(
    val status: String,
    val reasons: List<String>,
    val subsidyPercent: Double?,
)

data class SchemeAnswer(
    val found: Boolean,
    val displayText: String,
    val spokenText: String,
    val citations: List<Citation>,
    val matchedIds: List<String>,
)

data class Citation(
    val id: String,
    val name: String,
    val sourceUrl: String,
    val lastVerified: String,
    val reviewDue: String,
)

/**
 * BM25 retrieval plus deterministic eligibility rules.
 *
 * Mirrors `scheme_engine.py`. There is no language model in the answer path:
 * a model could invent an income limit, and a wrong income limit costs a user
 * a trip to a government office they did not need to make.
 */
class SchemeEngine(private val dataset: Dataset) {

    data class Dataset(
        val version: String,
        val lastVerified: String,
        val schemes: List<Scheme>,
    )

    private val documents: List<List<String>> = dataset.schemes.map { tokensFor(it) }
    private val averageLength: Double =
        if (documents.isEmpty()) 0.0 else documents.sumOf { it.size }.toDouble() / documents.size
    private val index: Map<String, Double> = buildIndex(documents)

    fun search(query: String, topK: Int = 3): List<Pair<Scheme, Double>> {
        val queryTokens = tokenize(query)
        if (queryTokens.isEmpty()) return emptyList()

        // A query made only of generic words cannot identify a scheme.
        val informative = queryTokens.filter { it !in GENERIC_TOKENS && index.containsKey(it) }
        if (informative.isEmpty()) return emptyList()

        val k1 = 1.5
        val b = 0.75
        val lowered = query.lowercase()
        val scored = mutableListOf<Pair<Scheme, Double>>()

        for ((position, scheme) in dataset.schemes.withIndex()) {
            val tokens = documents[position]
            val length = tokens.size.coerceAtLeast(1)
            val counts = tokens.groupingBy { it }.eachCount()

            var score = 0.0
            val matchedTokens = mutableSetOf<String>()
            for (token in queryTokens) {
                val idf = index[token] ?: continue
                val tf = counts[token] ?: continue
                matchedTokens.add(token)
                val denominator = tf + k1 * (1 - b + b * length / (averageLength.takeIf { it > 0 } ?: 1.0))
                score += idf * (tf * (k1 + 1)) / denominator
            }

            var aliasHit = false
            for (alias in scheme.aliases) {
                if (alias.isNotEmpty() && lowered.contains(alias.lowercase())) {
                    score += 4.0
                    aliasHit = true
                }
            }

            // One incidental shared word is not evidence that this is the scheme
            // the user means. Require two distinct content words, or an alias.
            if (!aliasHit && matchedTokens.size < 2) continue

            if (score > 0) scored.add(scheme to score)
        }

        return scored.sortedByDescending { it.second }.take(topK)
    }

    fun answer(query: String, profile: EligibilityProfile? = null): SchemeAnswer {
        val matches = search(query)
        if (matches.isEmpty() || matches.first().second < MIN_SCORE) {
            return SchemeAnswer(
                found = false,
                displayText = NOT_FOUND,
                spokenText = NOT_FOUND,
                citations = emptyList(),
                matchedIds = emptyList(),
            )
        }

        val primary = matches.first().first
        val eligibility = evaluate(primary, profile)
        val display = StringBuilder()
        val spoken = StringBuilder()

        display.append(primary.name).append("\n\n")
        spoken.append(primary.name).append(". ")
        display.append(primary.summary).append("\n\n")
        spoken.append(primary.summary).append(" ")

        if (eligibility.status != "unknown") {
            val verdict = when (eligibility.status) {
                "eligible" -> "Likely eligible"
                "not_eligible" -> "Not eligible on the facts supplied"
                else -> "Needs more information"
            }
            display.append("Eligibility check: ").append(verdict).append(".\n")
            spoken.append("Eligibility check: ").append(verdict).append(". ")
            for (reason in eligibility.reasons) {
                display.append("- ").append(reason).append("\n")
                spoken.append(reason).append(" ")
            }
            eligibility.subsidyPercent?.let {
                display.append("- Subsidy: ").append(formatNumber(it)).append("%\n")
                spoken.append("Subsidy ").append(formatNumber(it)).append(" percent. ")
            }
            display.append("\n")
        } else if (profile == null) {
            display.append("Eligibility check: not run. Add your details to check.\n\n")
        }

        if (primary.benefits.isNotEmpty()) {
            display.append("What you get\n")
            for (benefit in primary.benefits) {
                display.append("- ").append(benefit).append("\n")
                spoken.append(benefit).append(" ")
            }
            display.append("\n")
        }

        if (primary.documentsRequired.isNotEmpty()) {
            display.append("Documents to carry\n")
            for (document in primary.documentsRequired) {
                display.append("- ").append(document).append("\n")
                spoken.append("Document: ").append(document).append(". ")
            }
            display.append("\n")
        }

        if (primary.howToApply.isNotEmpty()) {
            display.append("How to apply\n")
            for (step in primary.howToApply) {
                display.append("- ").append(step).append("\n")
                spoken.append("Step: ").append(step).append(". ")
            }
            display.append("\n")
        }

        val stale = isStale(primary)
        display.append("Source: ").append(primary.sourceUrl).append("\n")
        display.append("Last verified: ").append(primary.lastVerified).append("\n")
        display.append("Review due: ").append(primary.reviewDue).append("\n")
        display.append("Status: ").append(primary.verificationStatus).append("\n")
        if (stale) {
            display.append(
                "\nThis record is past its review date. Confirm the current rules on the " +
                    "official portal before applying.\n"
            )
            spoken.append(
                "Warning. This record is past its review date. Confirm the current rules " +
                    "on the official portal before applying. "
            )
        }
        primary.helpline?.let {
            display.append("\nHelpline: ").append(it).append("\n")
            spoken.append("Helpline: ").append(it).append(". ")
        }
        display.append(
            "\nThis is an information aid, not a legal or financial decision. " +
                "The official portal is the final authority."
        )
        spoken.append("This is an information aid. The official portal is the final authority.")

        return SchemeAnswer(
            found = true,
            displayText = display.toString(),
            spokenText = spoken.toString(),
            citations = matches.map {
                Citation(
                    id = it.first.id,
                    name = it.first.name,
                    sourceUrl = it.first.sourceUrl,
                    lastVerified = it.first.lastVerified,
                    reviewDue = it.first.reviewDue,
                )
            },
            matchedIds = matches.map { it.first.id },
        )
    }

    fun evaluate(scheme: Scheme, profile: EligibilityProfile?): EligibilityResult {
        if (profile == null) {
            return EligibilityResult(
                status = "unknown",
                reasons = listOf("No profile supplied, so eligibility cannot be checked."),
                subsidyPercent = null,
            )
        }

        val reasons = mutableListOf<String>()
        var failed = false
        var unknown = false

        if (scheme.disabilityPercentMin > 0) {
            val percent = profile.disabilityPercent
            when {
                percent == null -> {
                    unknown = true
                    reasons.add("Disability percentage is required (minimum ${formatNumber(scheme.disabilityPercentMin)}%).")
                }
                percent < scheme.disabilityPercentMin -> {
                    failed = true
                    reasons.add("Disability is ${formatNumber(percent)}%, below the ${formatNumber(scheme.disabilityPercentMin)}% minimum.")
                }
                else -> reasons.add("Disability is at or above the ${formatNumber(scheme.disabilityPercentMin)}% minimum.")
            }
        }

        if (scheme.requiresUdid) {
            when (profile.hasUdid) {
                null -> {
                    unknown = true
                    reasons.add("UDID card status is required.")
                }
                false -> {
                    failed = true
                    reasons.add("A UDID card or UDID enrolment number is required.")
                }
                true -> reasons.add("UDID requirement is met.")
            }
        }

        if (scheme.requiresAadhaar) {
            when (profile.hasAadhaar) {
                null -> {
                    unknown = true
                    reasons.add("Aadhaar status is required.")
                }
                false -> {
                    failed = true
                    reasons.add("Aadhaar or an Aadhaar enrolment number is required.")
                }
                true -> reasons.add("Aadhaar requirement is met.")
            }
        }

        var subsidy: Double? = null
        if (scheme.incomeSlabs.isNotEmpty()) {
            val income = profile.monthlyIncomeInr
            if (income == null) {
                unknown = true
                reasons.add("Monthly family income is required to choose a subsidy slab.")
            } else {
                for (slab in scheme.incomeSlabs) {
                    val inRange = income >= slab.minMonthlyInr &&
                        (slab.maxMonthlyInr == null || income <= slab.maxMonthlyInr)
                    if (inRange) {
                        subsidy = slab.subsidyPercent
                        reasons.add(
                            "Monthly income ${formatNumber(income)} rupees falls in the " +
                                "${formatNumber(slab.subsidyPercent)}% subsidy slab."
                        )
                        break
                    }
                }
                if (subsidy == null) {
                    failed = true
                    reasons.add("Monthly income is above the highest subsidy slab.")
                }
            }
        }

        val status = when {
            failed -> "not_eligible"
            unknown -> "unknown"
            else -> "eligible"
        }
        return EligibilityResult(status, reasons, subsidy)
    }

    fun isStale(scheme: Scheme): Boolean = try {
        LocalDate.parse(scheme.reviewDue).isBefore(LocalDate.now())
    } catch (error: Exception) {
        true
    }

    companion object {
        /** Below this BM25 score the engine refuses to answer. */
        const val MIN_SCORE = 1.0

        private const val NOT_FOUND =
            "I could not find this in the verified scheme dataset, so I will not guess. " +
                "Try a scheme name such as ADIP, UDID or RPwD, or check depwd.gov.in."

        private val STOPWORDS = setOf(
            "a", "about", "also", "an", "and", "any", "are", "as", "at", "be", "by", "can",
            "do", "does", "exactly", "for", "from", "get", "give", "how", "i", "if", "in",
            "into", "is", "it", "its", "me", "much", "my", "no", "not", "of", "on", "or",
            "per", "please", "some", "that", "the", "there", "these", "this", "those", "to",
            "under", "what", "when", "where", "which", "who", "will", "with", "you",
        )

        private val GENERIC_TOKENS = setOf(
            "scheme", "schemes", "yojana", "government", "govt", "india", "indian",
            "disability", "disabilities", "disabled", "person", "persons", "people",
            "benefit", "benefits", "apply", "application", "document", "documents",
            "information", "details", "tell", "about", "help", "support", "available",
            "eligibility", "eligible", "need", "needs", "required", "requirement",
        )

        fun tokenize(text: String): List<String> {
            val lowered = text.lowercase()
                .replace("₹", " ")
                .replace("rs.", " ")
                .replace("rs", " ")
                .replace(Regex("[^\\w\\s/%-]"), " ")
            return lowered.split(Regex("\\s+"))
                .map { it.trim('/') }
                .filter { token ->
                    token.isNotEmpty() &&
                        token !in STOPWORDS &&
                        (token.length > 1 || token[0].isDigit())
                }
        }

        private fun tokensFor(scheme: Scheme): List<String> = tokenize(
            buildString {
                append(scheme.name).append(' ')
                append(scheme.aliases.joinToString(" ")).append(' ')
                append(scheme.category).append(' ')
                append(scheme.summary).append(' ')
                append(scheme.benefits.joinToString(" ")).append(' ')
                append(scheme.documentsRequired.joinToString(" ")).append(' ')
                append(scheme.howToApply.joinToString(" ")).append(' ')
                append(scheme.eligibilityNotes.joinToString(" "))
            }
        )

        private fun buildIndex(documents: List<List<String>>): Map<String, Double> {
            val documentCount = documents.size.coerceAtLeast(1)
            val frequencies = mutableMapOf<String, Int>()
            for (document in documents) {
                for (token in document.toSet()) {
                    frequencies[token] = (frequencies[token] ?: 0) + 1
                }
            }
            return frequencies.mapValues { (_, df) ->
                ln(1 + (documentCount - df + 0.5) / (df + 0.5))
            }
        }

        private fun formatNumber(value: Double): String =
            if (value % 1.0 == 0.0) {
                value.toLong().toString()
            } else {
                String.format(java.util.Locale.US, "%.1f", value)
            }

        /** Parse the bundled dataset. Throws with a clear message on malformed JSON. */
        fun load(context: Context, assetPath: String = "schemes/schemes.json"): Dataset {
            val text = context.assets.open(assetPath).bufferedReader().use { it.readText() }
            return parse(text)
        }

        /** Context-free parse, used by the JVM tests against the same asset. */
        fun parse(text: String): Dataset {
            val root = JSONObject(text)
            val array = root.getJSONArray("schemes")
            val schemes = ArrayList<Scheme>(array.length())
            for (i in 0 until array.length()) {
                schemes.add(parseScheme(array.getJSONObject(i)))
            }
            return Dataset(
                version = root.optString("dataset_version", "unknown"),
                lastVerified = root.optString("last_verified", "unknown"),
                schemes = schemes,
            )
        }

        private fun parseScheme(json: JSONObject): Scheme {
            val eligibility = json.getJSONObject("eligibility")
            val slabs = mutableListOf<IncomeSlab>()
            val slabArray = eligibility.optJSONArray("income_slabs") ?: JSONArray()
            for (i in 0 until slabArray.length()) {
                val slab = slabArray.getJSONObject(i)
                slabs.add(
                    IncomeSlab(
                        minMonthlyInr = slab.optDouble("min_monthly_inr", 0.0),
                        maxMonthlyInr = if (slab.has("max_monthly_inr") && !slab.isNull("max_monthly_inr")) {
                            slab.getDouble("max_monthly_inr")
                        } else {
                            null
                        },
                        subsidyPercent = slab.getDouble("subsidy_percent"),
                    )
                )
            }

            return Scheme(
                id = json.getString("id"),
                name = json.getString("name"),
                aliases = json.optJSONArray("aliases").toStringList(),
                category = json.optString("category", ""),
                summary = json.optString("summary", ""),
                benefits = json.optJSONArray("benefits").toStringList(),
                documentsRequired = json.optJSONArray("documents_required").toStringList(),
                howToApply = json.optJSONArray("how_to_apply").toStringList(),
                eligibilityNotes = eligibility.optJSONArray("notes").toStringList(),
                disabilityPercentMin = eligibility.optDouble("disability_percent_min", 0.0),
                requiresUdid = eligibility.optBoolean("requires_udid", false),
                requiresAadhaar = eligibility.optBoolean("requires_aadhaar", false),
                incomeSlabs = slabs,
                sourceUrl = json.getString("source_url"),
                lastVerified = json.getString("last_verified"),
                reviewDue = json.getString("review_due"),
                verificationStatus = json.optString("verification_status", "unverified"),
                helpline = json.optString("helpline").takeIf { it.isNotBlank() },
            )
        }

        private fun JSONArray?.toStringList(): List<String> {
            if (this == null) return emptyList()
            return List(length()) { getString(it) }
        }
    }
}
