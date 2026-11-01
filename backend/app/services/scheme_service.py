import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from backend.app.schemas.scheme import SchemeListItem, SchemeListResponse, SchemeDetailResponse, SchemeRecommendationRequest

logger = logging.getLogger("nitisetu.schemes")

# Resolve project data path
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
SCHEMES_FILE = BASE_DIR / "data" / "schemes" / "myscheme_central_state_schemes.json"
DOC_MATRIX_FILE = BASE_DIR / "data" / "document_requirements" / "scheme_document_matrix.json"


class SchemeCatalogService:
    def __init__(self):
        self._schemes: List[Dict] = []
        self._schemes_by_slug: Dict[str, Dict] = {}
        self._doc_matrix: Dict[str, Dict] = {}
        self._load_datasets()

    def _load_datasets(self):
        """Load authentic datasets from disk into memory."""
        try:
            if DOC_MATRIX_FILE.exists():
                with open(DOC_MATRIX_FILE, "r", encoding="utf-8") as f:
                    self._doc_matrix = json.load(f)
                logger.info(f"Loaded {len(self._doc_matrix)} scheme document matrix entries.")

            if SCHEMES_FILE.exists():
                with open(SCHEMES_FILE, "r", encoding="utf-8") as f:
                    raw_schemes = json.load(f)
                
                for s in raw_schemes:
                    slug = s.get("Scheme Slug") or s.get("Scheme Name", "").lower().replace(" ", "-")
                    # Clean slug
                    slug = slug.strip().strip("/")
                    s["_clean_slug"] = slug
                    self._schemes.append(s)
                    self._schemes_by_slug[slug] = s

                # Register canonical aliases for flagship hackathon demo schemes
                aliases = {
                    "national-scholarship-post-matric": "csspostmsossi",
                    "pm-usp-central-sector-scheme": "csspostmsossi",
                }
                for alias_slug, target_slug in aliases.items():
                    if target_slug in self._schemes_by_slug:
                        alias_scheme = dict(self._schemes_by_slug[target_slug])
                        alias_scheme["_clean_slug"] = alias_slug
                        alias_scheme["Scheme Name"] = "National Post-Matric Scholarship Scheme for SC/ST/OBC Students"
                        self._schemes_by_slug[alias_slug] = alias_scheme


                logger.info(f"Loaded {len(self._schemes)} authentic schemes from myScheme master.")
            else:
                logger.warning(f"Master schemes file not found at {SCHEMES_FILE}")
        except Exception as e:
            logger.error(f"Failed to load schemes dataset: {e}")

    def list_schemes(
        self,
        q: Optional[str] = None,
        state: Optional[str] = None,
        level: Optional[str] = None,
        scheme_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> SchemeListResponse:
        """Search and filter government schemes with pagination."""
        filtered = self._schemes

        # By default prioritize scholarships/education if scheme_type is 'scholarship'
        if scheme_type == "scholarship":
            filtered = [
                s for s in filtered
                if "scholarship" in s.get("Scheme Name", "").lower()
                or "scholarship" in s.get("Tags / Categories", "").lower()
                or "student" in s.get("Eligibility Criteria", "").lower()
                or "education" in s.get("Tags / Categories", "").lower()
            ]

        # Text search (query across name, tags, description, ministry)
        if q:
            query_lower = q.lower().strip()
            filtered = [
                s for s in filtered
                if query_lower in s.get("Scheme Name", "").lower()
                or query_lower in s.get("Tags / Categories", "").lower()
                or query_lower in s.get("Description", "").lower()
                or query_lower in s.get("State / UT / Ministry", "").lower()
            ]

        # State filter
        if state:
            state_lower = state.lower().strip()
            filtered = [
                s for s in filtered
                if s.get("Level", "") == "Central Government"
                or state_lower in s.get("State / UT / Ministry", "").lower()
            ]

        # Level filter (Central vs State)
        if level:
            level_lower = level.lower().strip()
            filtered = [s for s in filtered if level_lower in s.get("Level", "").lower()]

        total = len(filtered)
        start = (page - 1) * page_size
        end = start + page_size
        paged_items = filtered[start:end]

        items = []
        for s in paged_items:
            slug = s["_clean_slug"]
            desc = s.get("Description", "") or ""
            summary = desc[:250] + ("..." if len(desc) > 250 else "")

            items.append(SchemeListItem(
                id=slug,
                slug=slug,
                name=s.get("Scheme Name", "Untitled Scheme"),
                summary=summary,
                level=s.get("Level", "Central Government"),
                state_or_ministry=s.get("State / UT / Ministry"),
                scheme_type="scholarship" if "scholarship" in s.get("Scheme Name", "").lower() else "welfare",
                application_mode=s.get("Application Mode", "Online"),
                benefit_summary=(s.get("Benefits", "") or "")[:200],
                official_url=s.get("Official Link") or s.get("MyScheme URL") or "https://www.myscheme.gov.in/",
                last_verified_at="2024-11-01"
            ))

        return SchemeListResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=items
        )

    def get_scheme_by_slug(self, slug: str) -> Optional[SchemeDetailResponse]:
        """Fetch full authentic scheme details by unique slug."""
        clean_slug = slug.strip().strip("/")
        s = self._schemes_by_slug.get(clean_slug)
        if not s:
            # Fallback search by partial slug or ID
            for item in self._schemes:
                if item["_clean_slug"] == clean_slug or item.get("Scheme Slug") == clean_slug:
                    s = item
                    break

        if not s:
            return None

        # Look up document tags from document matrix
        matrix_entry = self._doc_matrix.get(clean_slug, self._doc_matrix.get(s.get("Scheme Slug", ""), {}))
        detected_docs = matrix_entry.get("detected_document_tags", [])
        if not detected_docs:
            docs_text = (s.get("Documents Required", "") or "").lower()
            doc_keywords = {
                "aadhaar_card": ["aadhaar", "aadhar", "uid"],
                "income_certificate": ["income certificate", "income proof", "salary"],
                "caste_category_certificate": ["caste", "community certificate", "obc", "sc/st"],
                "educational_marksheets": ["marksheet", "qualification", "degree", "certificate"],
                "bank_passbook_account": ["bank", "passbook", "account"],
                "bonafide_student_certificate": ["bonafide", "college", "school", "institution"]
            }
            detected_docs = [tag for tag, kws in doc_keywords.items() if any(k in docs_text for k in kws)]
            if not detected_docs and ("scholarship" in s.get("Scheme Name", "").lower()):
                detected_docs = ["aadhaar_card", "income_certificate", "educational_marksheets", "bonafide_student_certificate"]


        desc = s.get("Description", "") or ""
        summary = desc[:300] + ("..." if len(desc) > 300 else "")

        return SchemeDetailResponse(
            id=s["_clean_slug"],
            slug=s["_clean_slug"],
            name=s.get("Scheme Name", "Untitled Scheme"),
            summary=summary,
            description=desc,
            level=s.get("Level", "Central Government"),
            state_or_ministry=s.get("State / UT / Ministry"),
            scheme_type="scholarship" if "scholarship" in s.get("Scheme Name", "").lower() else "welfare",
            application_mode=s.get("Application Mode", "Online"),
            benefit_summary=s.get("Benefits"),
            eligibility_criteria_text=s.get("Eligibility Criteria") or s.get("Eligibility (General)"),
            exclusions_text=s.get("Exclusions / Ineligibility"),
            application_process_text=s.get("Application Process"),
            documents_required_text=s.get("Documents Required"),
            detected_document_tags=detected_docs,
            faqs=s.get("Frequently Asked Questions (FAQs)"),
            official_url=s.get("Official Link") or s.get("MyScheme URL") or "https://www.myscheme.gov.in/",
            application_url=s.get("Official Link"),
            last_verified_at="2024-11-01"
        )

    def get_recommendations(self, profile: SchemeRecommendationRequest) -> List[SchemeListItem]:
        """Recommend schemes and scholarships based on user profile facts with plain match reasons."""
        candidates = []

        for s in self._schemes:
            score = 0
            reasons = []

            name_lower = s.get("Scheme Name", "").lower()
            tags_lower = s.get("Tags / Categories", "").lower()
            elig_lower = (s.get("Eligibility Criteria", "") or "").lower()
            state_lower = (s.get("State / UT / Ministry", "") or "").lower()
            level = s.get("Level", "")

            # 1. State matching
            if profile.state_code:
                usr_state = profile.state_code.lower()
                if usr_state in state_lower:
                    score += 30
                    reasons.append(f"Specific to {profile.state_code}")
                elif level == "Central Government":
                    score += 15
                    reasons.append("Available nationally (Central Government)")
                else:
                    # Scheme is for another state
                    continue
            else:
                if level == "Central Government":
                    score += 10

            # 2. Occupation & Livelihood matching
            if profile.occupation:
                occ_clean = profile.occupation.lower()
                if "farmer" in occ_clean or "agri" in occ_clean:
                    if "kisan" in name_lower or "farmer" in name_lower or "agriculture" in tags_lower or "crop" in elig_lower:
                        score += 35
                        reasons.append("Designed for farmers & agricultural cultivators")
                elif "artisan" in occ_clean or "craft" in occ_clean:
                    if "vishwakarma" in name_lower or "artisan" in elig_lower or "craft" in tags_lower:
                        score += 35
                        reasons.append("Targeted for traditional artisans and craftspersons")
                elif "vendor" in occ_clean or "street" in occ_clean:
                    if "svanidhi" in name_lower or "vendor" in elig_lower or "micro" in tags_lower:
                        score += 35
                        reasons.append("Specialized credit/subsidy for urban & street vendors")
                elif "senior" in occ_clean or "retired" in occ_clean:
                    if "pension" in name_lower or "old age" in elig_lower or "senior" in tags_lower:
                        score += 35
                        reasons.append("Social security & pension support for senior citizens")
                elif "student" in occ_clean:
                    if "scholarship" in name_lower or "fellowship" in name_lower or "education" in tags_lower:
                        score += 30
                        reasons.append("Financial assistance & scholarships for students")

            # 3. Landowner matching
            if profile.is_landowner:
                if "kisan" in name_lower or "land" in elig_lower or "fasal" in name_lower:
                    score += 25
                    reasons.append("Eligible as agricultural landowner")

            # 4. Age matching
            if profile.age is not None:
                if profile.age >= 60:
                    if "senior" in tags_lower or "pension" in name_lower or "vridha" in name_lower:
                        score += 25
                        reasons.append("Matches senior citizen age threshold (60+ years)")
                elif profile.age <= 35:
                    if "youth" in tags_lower or "employment" in tags_lower or "skill" in tags_lower:
                        score += 15
                        reasons.append("Targeted for youth & skill development")

            # 5. Ration card / Food Security matching
            if profile.ration_card_type:
                rc_lower = profile.ration_card_type.lower()
                if "antyodaya" in rc_lower or "aay" in rc_lower or "bpl" in rc_lower:
                    if "ayushman" in name_lower or "bpl" in elig_lower or "ration" in tags_lower or "pm-jay" in name_lower:
                        score += 30
                        reasons.append("Qualifies under NFSA / Priority Household entitlement")

            # 6. Education matching
            if profile.education_level:
                edu_clean = profile.education_level.lower()
                if "scholarship" in name_lower or "scholarship" in tags_lower:
                    score += 20
                    reasons.append("Targeted for education & training assistance")
                if "undergraduate" in edu_clean or "college" in edu_clean or "12th" in edu_clean:
                    if "higher education" in elig_lower or "post-matric" in elig_lower or "college" in elig_lower:
                        score += 15
                        reasons.append(f"Matches your educational stage ({profile.education_level})")

            # 7. Caste / Category matching
            if profile.caste_category:
                cat_lower = profile.caste_category.lower()
                if cat_lower != "general":
                    if cat_lower in elig_lower or cat_lower in name_lower or cat_lower in tags_lower:
                        score += 25
                        reasons.append(f"Dedicated provisions for {profile.caste_category}")

            # 8. Income matching
            if profile.annual_family_income is not None:
                if profile.annual_family_income <= 250000:
                    if "low income" in elig_lower or "bpl" in elig_lower or "means" in name_lower or "2,50,000" in elig_lower:
                        score += 20
                        reasons.append("Qualifies under low-income / means-tested threshold")
                elif profile.annual_family_income <= 450000:
                    if "4,50,000" in elig_lower or "merit-cum-means" in name_lower:
                        score += 15
                        reasons.append("Matches income threshold under ₹4.5 Lakh")

            # 9. Differently Abled matching
            if profile.is_differently_abled:
                if "disab" in elig_lower or "differently abled" in elig_lower or "handicapped" in elig_lower:
                    score += 35
                    reasons.append("Includes specialized disability support / reservation")

            # 10. Gender matching
            if profile.gender and profile.gender.lower() == "female":
                if "girl" in name_lower or "women" in name_lower or "female" in elig_lower or "mahila" in name_lower:
                    score += 25
                    reasons.append("Special benefits for women / girl children")

            if score > 0:
                slug = s["_clean_slug"]
                reason_str = "; ".join(reasons[:2]) if reasons else "Matches your demographic profile"
                candidates.append((score, s, reason_str))

        # Sort candidates by match score descending
        candidates.sort(key=lambda x: x[0], reverse=True)

        results = []
        for _, s, reason in candidates[:profile.limit]:
            slug = s["_clean_slug"]
            desc = s.get("Description", "") or ""
            summary = desc[:200] + ("..." if len(desc) > 200 else "")

            results.append(SchemeListItem(
                id=slug,
                slug=slug,
                name=s.get("Scheme Name", "Untitled Scheme"),
                summary=summary,
                level=s.get("Level", "Central Government"),
                state_or_ministry=s.get("State / UT / Ministry"),
                scheme_type="scholarship" if "scholarship" in s.get("Scheme Name", "").lower() else "welfare",
                application_mode=s.get("Application Mode", "Online"),
                benefit_summary=(s.get("Benefits", "") or "")[:200],
                official_url=s.get("Official Link") or s.get("MyScheme URL") or "https://www.myscheme.gov.in/",
                last_verified_at="2024-11-01",
                recommendation_reason=reason
            ))

        return results


scheme_service = SchemeCatalogService()

