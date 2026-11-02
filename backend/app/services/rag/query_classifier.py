import re


class QueryClassifier:
    """Classifies user welfare inquiries into structured intent categories for targeted retrieval."""

    INTENT_LABELS = {
        "exclusions": "Exclusion & Ineligibility Rules",
        "income": "Income Ceiling & Means Threshold",
        "eligibility": "Eligibility & Criteria Check",
        "documents": "Mandatory Documentation Requirements",
        "benefits": "Financial Benefits & Subsidy Structure",
        "steps": "Step-by-Step Application Procedure",
        "deadline": "Deadlines & Timelines",
        "institution": "Institution & Course Recognition Criteria",
        "general": "General Scheme Overview"
    }

    def classify(self, question: str) -> str:
        q = question.lower()

        # 1. Statutory Exclusions & Ineligibility (Strict Priority)
        if any(w in q for w in [
            "income tax", "tax payer", "taxpayer", "itr", "government employee", "govt employee",
            "civil servant", "institutional landholder", "ineligible", "exclusion", "excluded",
            "cannot apply", "disqualified", "not eligible", "two scholarships", "dual scholarship",
            "another scholarship", "simultaneously", "both scholarship", "bar", "prohibited", "restriction"
        ]):
            return "exclusions"

        # 2. Deadlines & Schedule
        if any(w in q for w in ["deadline", "last date", "due date", "closing date", "schedule", "akhri date", "antim tithi"]):
            return "deadline"

        # 3. Income & Means Threshold
        if any(w in q for w in ["income", "ceiling", "salary", "earning", "creamy layer", "annual limit", "lakh", "kamai", "aay seema"]):
            return "income"

        # 4. Age Limit & General Eligibility
        if any(w in q for w in [
            "age limit", "age", "old", "cutoff", "percentile", "marks", "caste", "patrata",
            "qualify", "who can apply", "eligible", "eligibility", "kya mai", "am i eligible"
        ]):
            return "eligibility"

        # 5. Financial Benefits, Amounts & Subsidies
        if any(w in q for w in [
            "benefit", "benefits", "amount", "how much", "financial", "stipend", "allowance",
            "subsidy", "cashless", "loan", "installment", "cashback", "kitna paisa",
            "kitna milega", "kitna milta", "paisa", "rupee", "kist", "pension amount",
            "how much pension", "guaranteed pension"
        ]):
            return "benefits"

        # 6. Documents & Checklist
        if any(w in q for w in [
            "document", "documents", "certificate", "aadhaar", "marksheet", "bonafide",
            "passbook", "proof", "papers", "kagaj", "praman patra", "dastavej"
        ]):
            return "documents"

        # 7. Application Steps & Procedure
        if any(w in q for w in [
            "apply", "application", "steps", "procedure", "how to apply", "registration",
            "otr", "portal", "kaise apply", "kaise bhare", "process", "kaise milega"
        ]):
            return "steps"

        # 8. Institution & Course Accreditation
        if any(w in q for w in ["college", "university", "institute", "naac", "aicte", "ugc", "recognized", "accreditation"]):
            return "institution"

        return "general"

    def get_intent_label(self, intent_code: str) -> str:
        return self.INTENT_LABELS.get(intent_code, "General Scheme Information")


query_classifier = QueryClassifier()
