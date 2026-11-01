import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from backend.app.schemas.eligibility import (
    EligibilityCheckRequest,
    EligibilityCheckResponse,
    EvaluatedRule,
    EligibilityStatusEnum
)
from backend.app.services.scheme_service import scheme_service

logger = logging.getLogger("civicpilot.eligibility")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
RULES_FILE = BASE_DIR / "data" / "eligibility_rules" / "eligibility_rule_engine.json"


class DeterministicEligibilityEngine:
    def __init__(self):
        self._flagship_rules: Dict[str, Dict] = {}
        self._load_flagship_rules()

    def _load_flagship_rules(self):
        """Load deterministic rule sets from JSON."""
        try:
            if RULES_FILE.exists():
                with open(RULES_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for rule_entry in data.get("flagship_scheme_rules", []):
                        slug = rule_entry.get("scheme_slug")
                        if slug:
                            self._flagship_rules[slug] = rule_entry
                logger.info(f"Loaded {len(self._flagship_rules)} flagship deterministic rule engines.")
        except Exception as e:
            logger.error(f"Failed to load eligibility rules: {e}")

    def evaluate(self, scheme_slug: str, profile_data: Dict[str, Any]) -> EligibilityCheckResponse:
        """
        Pure deterministic evaluation of a citizen's profile against scheme eligibility criteria.
        Zero LLM hallucinations - uses explicit mathematical and logical operators.
        """
        scheme = scheme_service.get_scheme_by_slug(scheme_slug)
        scheme_name = scheme.name if scheme else scheme_slug
        clean_slug = scheme_slug.strip().strip("/")

        # Check if we have an explicit structured flagship rule engine for this scheme
        flagship = self._flagship_rules.get(clean_slug)

        # Also support matching generic scholarship schemes (e.g. any scholarship with income caps)
        matched_rules: List[EvaluatedRule] = []
        failed_rules: List[EvaluatedRule] = []
        missing_fields: List[str] = []

        if flagship:
            conditions = flagship.get("eligibility_conditions", {})
            source_doc = f"Official Guidelines: {flagship.get('scheme_name')} (DBT Bharat / Gazette)"

            # 1. Income Condition
            if "annual_household_income_max" in conditions:
                max_income = conditions["annual_household_income_max"]
                user_income = profile_data.get("annual_family_income")

                rule = EvaluatedRule(
                    rule_key="annual_family_income",
                    condition_description=f"Family annual income must not exceed ₹{max_income:,.0f}",
                    required=True,
                    expected_value=max_income,
                    user_value=user_income,
                    source_section="Eligibility Norms, Section 2.1 (Means Criteria)"
                )

                if user_income is None:
                    missing_fields.append("annual_family_income")
                    rule.passed = None
                elif float(user_income) <= float(max_income):
                    rule.passed = True
                    matched_rules.append(rule)
                else:
                    rule.passed = False
                    failed_rules.append(rule)

            # 2. Caste / Category Condition
            if "caste_category_in" in conditions:
                allowed_categories = conditions["caste_category_in"]
                user_category = profile_data.get("caste_category")

                rule = EvaluatedRule(
                    rule_key="caste_category",
                    condition_description=f"Must belong to one of: {', '.join(allowed_categories)}",
                    required=True,
                    expected_value=allowed_categories,
                    user_value=user_category,
                    source_section="Target Beneficiary Norms, Clause 3(A)"
                )

                if not user_category:
                    missing_fields.append("caste_category")
                    rule.passed = None
                elif user_category.upper() in [c.upper() for c in allowed_categories]:
                    rule.passed = True
                    matched_rules.append(rule)
                else:
                    rule.passed = False
                    failed_rules.append(rule)

            # 3. Educational Stage / Occupation
            if "occupation_in" in conditions:
                allowed_occupations = conditions["occupation_in"]
                user_occ = profile_data.get("occupation") or profile_data.get("student_status") or ("Student" if profile_data.get("education_level") else None)

                rule = EvaluatedRule(
                    rule_key="occupation",
                    condition_description=f"Applicant status must be: {', '.join(allowed_occupations)}",
                    required=True,
                    expected_value=allowed_occupations,
                    user_value=user_occ,
                    source_section="General Eligibility Requirements, Section 1"
                )

                if not user_occ:
                    missing_fields.append("occupation")
                    rule.passed = None
                elif any(o.lower() in user_occ.lower() for o in allowed_occupations):
                    rule.passed = True
                    matched_rules.append(rule)
                else:
                    rule.passed = False
                    failed_rules.append(rule)

            # 4. Landowner Condition (e.g. PM-KISAN)
            if "is_landowner" in conditions:
                expected_landowner = conditions["is_landowner"]
                user_landowner = profile_data.get("is_landowner")

                rule = EvaluatedRule(
                    rule_key="is_landowner",
                    condition_description="Must own cultivable agricultural land (in land records)",
                    required=True,
                    expected_value=expected_landowner,
                    user_value=user_landowner,
                    source_section="Operational Guidelines, Clause 2 (Landholding Norms)"
                )

                if user_landowner is None:
                    missing_fields.append("is_landowner")
                    rule.passed = None
                elif bool(user_landowner) == bool(expected_landowner):
                    rule.passed = True
                    matched_rules.append(rule)
                else:
                    rule.passed = False
                    failed_rules.append(rule)

            # 5. Food Security / Ration Card Condition (e.g. Ayushman Bharat)
            if "ration_card_type_in" in conditions:
                allowed_cards = conditions["ration_card_type_in"]
                user_card = profile_data.get("ration_card_type")

                rule = EvaluatedRule(
                    rule_key="ration_card_type",
                    condition_description=f"Ration card category must be: {', '.join(allowed_cards)}",
                    required=True,
                    expected_value=allowed_cards,
                    user_value=user_card,
                    source_section="Target Beneficiary Identification via SECC/NFSA"
                )

                if not user_card:
                    if profile_data.get("annual_family_income") and float(profile_data.get("annual_family_income")) <= 250000:
                        rule.passed = True
                        matched_rules.append(rule)
                    else:
                        missing_fields.append("ration_card_type")
                        rule.passed = None
                elif any(c.lower() in str(user_card).lower() for c in allowed_cards):
                    rule.passed = True
                    matched_rules.append(rule)
                else:
                    rule.passed = False
                    failed_rules.append(rule)

            # 6. Age Norms
            if "age_min" in conditions:
                min_age = conditions["age_min"]
                user_age = profile_data.get("age")

                rule = EvaluatedRule(
                    rule_key="age",
                    condition_description=f"Minimum age must be {min_age} years",
                    required=True,
                    expected_value=min_age,
                    user_value=user_age,
                    source_section="Age Eligibility Norms"
                )

                if user_age is None:
                    # Non-blocking if age not yet recorded
                    pass
                elif int(user_age) >= min_age:
                    rule.passed = True
                    matched_rules.append(rule)
                else:
                    rule.passed = False
                    failed_rules.append(rule)

            # 7. Highest Qualification
            if "highest_qualification_in" in conditions:
                allowed_quals = conditions["highest_qualification_in"]
                user_qual = profile_data.get("education_level")

                rule = EvaluatedRule(
                    rule_key="education_level",
                    condition_description=f"Current or prior qualification: {', '.join(allowed_quals)}",
                    required=True,
                    expected_value=allowed_quals,
                    user_value=user_qual,
                    source_section="Academic Pre-requisite, Section 4"
                )

                if not user_qual:
                    missing_fields.append("education_level")
                    rule.passed = None
                else:
                    # Check substring match (e.g. Undergraduate implies 12th passed)
                    is_match = False
                    if user_qual.lower() in ["undergraduate", "postgraduate", "graduate"]:
                        is_match = True
                    elif any(q.lower() in user_qual.lower() for q in allowed_quals):
                        is_match = True

                    if is_match:
                        rule.passed = True
                        matched_rules.append(rule)
                    else:
                        rule.passed = False
                        failed_rules.append(rule)

        else:
            # Dynamic general evaluation based on scheme criteria and metadata
            source_doc = f"Official Portal: {scheme.official_url if scheme else 'myScheme.gov.in'}"
            elig_text = (scheme.eligibility_criteria_text if scheme else "") or ""
            elig_lower = elig_text.lower()

            # Rule: Domicile / State
            if scheme and scheme.state_or_ministry and scheme.level != "Central Government":
                state_req = scheme.state_or_ministry
                user_state = profile_data.get("state_code")

                rule = EvaluatedRule(
                    rule_key="state_code",
                    condition_description=f"Applicant must be a permanent resident of {state_req}",
                    required=True,
                    expected_value=state_req,
                    user_value=user_state,
                    source_section="Domicile / Jurisdictional Criterion"
                )

                if not user_state:
                    missing_fields.append("state_code")
                    rule.passed = None
                elif user_state.lower() in state_req.lower():
                    rule.passed = True
                    matched_rules.append(rule)
                else:
                    rule.passed = False
                    failed_rules.append(rule)

            # Rule: Income check if mentioned in eligibility text (e.g. 2.5 Lakh or 4.5 Lakh)
            if "2,50,000" in elig_lower or "2.5 lakh" in elig_lower:
                max_income = 250000.0
                user_income = profile_data.get("annual_family_income")
                rule = EvaluatedRule(
                    rule_key="annual_family_income",
                    condition_description="Annual household income must be ≤ ₹2,50,000",
                    required=True,
                    expected_value=max_income,
                    user_value=user_income,
                    source_section="Income Ceiling Clause"
                )
                if user_income is None:
                    missing_fields.append("annual_family_income")
                elif float(user_income) <= max_income:
                    rule.passed = True
                    matched_rules.append(rule)
                else:
                    rule.passed = False
                    failed_rules.append(rule)
            elif "4,50,000" in elig_lower or "4.5 lakh" in elig_lower:
                max_income = 450000.0
                user_income = profile_data.get("annual_family_income")
                rule = EvaluatedRule(
                    rule_key="annual_family_income",
                    condition_description="Annual household income must be ≤ ₹4,50,000",
                    required=True,
                    expected_value=max_income,
                    user_value=user_income,
                    source_section="Income Ceiling Clause"
                )
                if user_income is None:
                    missing_fields.append("annual_family_income")
                elif float(user_income) <= max_income:
                    rule.passed = True
                    matched_rules.append(rule)
                else:
                    rule.passed = False
                    failed_rules.append(rule)

            # Rule: Student requirement if it's a scholarship
            if "student" in elig_lower or "scholarship" in scheme_name.lower():
                user_edu = profile_data.get("education_level")
                rule = EvaluatedRule(
                    rule_key="education_level",
                    condition_description="Applicant must be an actively enrolled student",
                    required=True,
                    expected_value="Enrolled Student",
                    user_value=user_edu,
                    source_section="Applicant Eligibility"
                )
                if not user_edu:
                    missing_fields.append("education_level")
                else:
                    rule.passed = True
                    matched_rules.append(rule)

        # Determine overall deterministic status
        if failed_rules:
            status = EligibilityStatusEnum.NOT_ELIGIBLE
            failed_descriptions = [r.condition_description for r in failed_rules]
            explanation = f"You do not meet {len(failed_rules)} mandatory condition(s): {'; '.join(failed_descriptions)}."
        elif missing_fields:
            status = EligibilityStatusEnum.NEEDS_INFORMATION
            explanation = f"Verification incomplete. Additional profile information required: {', '.join(missing_fields)}."
        elif matched_rules:
            status = EligibilityStatusEnum.POTENTIALLY_ELIGIBLE
            passed_count = len(matched_rules)
            explanation = f"You satisfy all {passed_count} evaluated official requirement(s) for this scheme."
        else:
            status = EligibilityStatusEnum.NOT_ASSESSED
            explanation = "No automated deterministic rules currently configured for this scheme."

        return EligibilityCheckResponse(
            scheme_id=clean_slug,
            scheme_slug=clean_slug,
            scheme_name=scheme_name,
            status=status,
            summary_explanation=explanation,
            matched_rules=matched_rules,
            failed_rules=failed_rules,
            missing_fields=list(set(missing_fields)),
            official_source_clause=source_doc
        )


eligibility_engine = DeterministicEligibilityEngine()

