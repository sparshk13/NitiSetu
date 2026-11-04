import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from backend.app.schemas.scheme import SchemeListItem, SchemeListResponse, SchemeDetailResponse, SchemeRecommendationRequest

logger = logging.getLogger("nitisetu.schemes")

# Resolve project data path
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
SCHEMES_FILE = BASE_DIR / "data" / "schemes" / "myscheme_central_state_schemes.json"
DOC_MATRIX_FILE = BASE_DIR / "data" / "documents" / "scheme_document_matrix.json"


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

                # Register canonical aliases for flagship demo schemes
                aliases = {
                    "national-scholarship-post-matric": "csspostmsossi",
                    "pm-usp-central-sector-scheme": "csspostmsossi",
                    "pm-vishwakarma": "pmv",
                    "pm-surya-ghar-muft-bijli": "pmsgmb",
                    "pm-awas-yojana": "pmay-u",
                    "pmay": "pmay-u",
                    "pmay-urban": "pmay-u",
                    "pmay-gramin": "pmay-u",
                    "kisan-credit-card": "kcc",
                    "mudra": "pmmy",
                    "sukanya-samriddhi-yojana": "ssy",
                    "atal-pension-yojana": "apy",
                }
                for alias_slug, target_slug in aliases.items():
                    if target_slug in self._schemes_by_slug:
                        alias_scheme = dict(self._schemes_by_slug[target_slug])
                        alias_scheme["_clean_slug"] = alias_slug
                        if alias_slug == "national-scholarship-post-matric":
                            alias_scheme["Scheme Name"] = "National Post-Matric Scholarship Scheme for SC/ST/OBC Students"
                        elif alias_slug == "pm-vishwakarma":
                            alias_scheme["Scheme Name"] = "PM Vishwakarma"
                        elif alias_slug == "pm-surya-ghar-muft-bijli":
                            alias_scheme["Scheme Name"] = "PM - Surya Ghar: Muft Bijli Yojana"
                        elif alias_slug == "pm-awas-yojana":
                            alias_scheme["Scheme Name"] = "Pradhan Mantri Awas Yojana (PMAY)"
                        self._schemes_by_slug[alias_slug] = alias_scheme

                # Ensure Ayushman Bharat is registered
                if "ayushman-bharat-pmjay" not in self._schemes_by_slug:
                    ayushman_scheme = {
                        "_clean_slug": "ayushman-bharat-pmjay",
                        "Scheme Slug": "ayushman-bharat-pmjay",
                        "Scheme Name": "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana (PM-JAY)",
                        "Level": "Central Government",
                        "State / UT / Ministry": "National Health Authority, Ministry of Health & Family Welfare",
                        "Brief Description": "World's largest healthcare assurance scheme offering ₹5,00,000 cashless hospitalization cover per family per year.",
                        "Description": "Ayushman Bharat PM-JAY is the world's largest government-funded health assurance scheme targeting over 12 crore poor and vulnerable families (bottom 40% of the population) providing ₹5,00,000 per family per year for secondary and tertiary care hospitalization across all empanelled hospitals.",
                        "Eligibility Criteria": "Families identified via SECC 2011 deprivation criteria in rural areas and occupational criteria in urban areas, and NFSA ration card holders. No family size, age, or gender limits.",
                        "Exclusions": "Families covered under statutory corporate health insurance schemes or income tax payees not on SECC deprivation list.",
                        "Benefits": "₹5,00,000 per family per year cashless hospitalization coverage at empanelled public and private hospitals nationwide. Includes pre- and post-hospitalization costs and all pre-existing conditions from Day 1.",
                        "Documents Required": "Aadhaar Card, Ration Card (NFSA / SECC linked), PMJAY Golden Card / ABHA Card, Active Mobile Number.",
                        "Application Process": "Visit nearest CSC, empanelled hospital (Pradhan Mantri Arogya Mitra desk), or beneficiary.nha.gov.in portal to verify eligibility and generate Ayushman Card.",
                        "Official Portal": "https://beneficiary.nha.gov.in/",
                        "Tags / Categories": "Health, Medical, Hospitalization, Insurance, Healthcare"
                    }
                    self._schemes.append(ayushman_scheme)
                    self._schemes_by_slug["ayushman-bharat-pmjay"] = ayushman_scheme
                    self._schemes_by_slug["pmjay"] = ayushman_scheme
                    self._schemes_by_slug["ayushman-card"] = ayushman_scheme


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
        """Search and filter government schemes with multi-token matching and pagination."""
        filtered = self._schemes

        # Scheme Type / Sector Filter
        if scheme_type and scheme_type.strip():
            st = scheme_type.lower().strip()
            if st == "scholarship":
                filtered = [
                    s for s in filtered
                    if "scholarship" in s.get("Scheme Name", "").lower()
                    or "scholarship" in s.get("Tags / Categories", "").lower()
                    or "student" in s.get("Eligibility Criteria", "").lower()
                    or "education" in s.get("Tags / Categories", "").lower()
                ]
            elif st in ("farmer", "agriculture"):
                filtered = [
                    s for s in filtered
                    if any(k in f"{s.get('Scheme Name','')} {s.get('Tags / Categories','')} {s.get('Description','')}".lower() 
                           for k in ["farmer", "kisan", "krishi", "agriculture", "crop", "cultivat", "soil", "pm-kisan"])
                ]
            elif st in ("health", "wellness"):
                filtered = [
                    s for s in filtered
                    if any(k in f"{s.get('Scheme Name','')} {s.get('Tags / Categories','')} {s.get('Description','')}".lower() 
                           for k in ["health", "hospital", "ayushman", "swasthya", "medical", "insurance", "treatment"])
                ]
            elif st in ("pension", "senior"):
                filtered = [
                    s for s in filtered
                    if any(k in f"{s.get('Scheme Name','')} {s.get('Tags / Categories','')} {s.get('Description','')}".lower() 
                           for k in ["pension", "old age", "vridha", "senior", "social security", "divyang pension", "atal pension"])
                ]
            elif st in ("housing", "shelter"):
                filtered = [
                    s for s in filtered
                    if any(k in f"{s.get('Scheme Name','')} {s.get('Tags / Categories','')} {s.get('Description','')}".lower() 
                           for k in ["awas", "housing", "pucca", "shelter", "ghar", "residential"])
                ]
            elif st in ("business", "msme", "loan"):
                filtered = [
                    s for s in filtered
                    if any(k in f"{s.get('Scheme Name','')} {s.get('Tags / Categories','')} {s.get('Description','')}".lower() 
                           for k in ["business", "msme", "mudra", "subsidy", "credit", "entrepreneur", "loan", "startup"])
                ]
            elif st in ("worker", "artisan", "labor"):
                filtered = [
                    s for s in filtered
                    if any(k in f"{s.get('Scheme Name','')} {s.get('Tags / Categories','')} {s.get('Description','')}".lower() 
                           for k in ["artisan", "vishwakarma", "svanidhi", "vendor", "craft", "worker", "shramik", "labor", "skill"])
                ]

        # Multi-token text search with alias recognition and relevance ranking
        if q and q.strip():
            raw_q = q.lower().strip()
            clean_q = re.sub(r'[^a-z0-9\s]', ' ', raw_q)
            tokens = [t for t in clean_q.split() if len(t) >= 2]

            scored_schemes = []
            for s in filtered:
                slug = s.get("_clean_slug", "").lower()
                name = s.get("Scheme Name", "").lower()
                clean_name = re.sub(r'[^a-z0-9\s]', ' ', name)
                name_words = set(clean_name.split())
                tags = s.get("Tags / Categories", "").lower()
                desc = s.get("Description", "").lower()
                ministry = s.get("State / UT / Ministry", "").lower()
                blob = f"{slug} {name} {tags} {desc} {ministry}"

                score = 0

                # 1. Exact slug match or clean slug match
                if raw_q == slug or raw_q.replace("-", "") == slug.replace("-", ""):
                    score += 200
                elif slug.startswith(raw_q):
                    score += 90

                # 2. Exact phrase match in scheme name
                if raw_q in name:
                    score += 150
                    if name.startswith(raw_q):
                        score += 50

                # 3. All tokens in scheme name
                if tokens and all(t in name_words or any(w.startswith(t) for w in name_words) for t in tokens):
                    score += 100
                elif tokens and all(t in blob for t in tokens):
                    score += 40

                # 4. Partial token matches in name
                for t in tokens:
                    if t in name_words:
                        score += 25
                    elif t in blob:
                        score += 5

                # 5. Targeted alias recognition
                if "kcc" in tokens or "kisan credit" in raw_q:
                    if slug == "kcc" or "kisan credit card" in name:
                        score += 180
                elif ("pmkisan" in clean_q or "pm kisan" in clean_q or "kisan samman" in clean_q) and slug == "pm-kisan":
                    score += 180
                elif ("mudra" in clean_q or "pmmy" in clean_q) and (slug == "pmmy" or "mudra yojana" in name):
                    score += 180
                elif ("sukanya" in clean_q or "ssy" in clean_q) and (slug == "ssy" or "sukanya samriddhi" in name):
                    score += 180
                elif ("atal pension" in clean_q or "apy" in clean_q) and (slug == "apy" or "atal pension" in name):
                    score += 180
                elif ("ayushman" in clean_q or "pmjay" in clean_q) and (slug == "ayushman-bharat-pmjay" or "pradhan mantri jan arogya" in name):
                    score += 180
                elif ("surya ghar" in clean_q or "muft bijli" in clean_q) and slug == "pm-surya-ghar-muft-bijli":
                    score += 180
                elif ("svanidhi" in clean_q or "street vendor" in clean_q) and slug == "pm-svanidhi":
                    score += 180
                elif "vishwakarma" in clean_q and slug == "pm-vishwakarma":
                    score += 180

                if score > 0:
                    scored_schemes.append((s, score))

            scored_schemes.sort(key=lambda x: x[1], reverse=True)
            filtered = [item[0] for item in scored_schemes]

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

        return SchemeListResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[self._to_list_item(s, summary_len=250) for s in paged_items]
        )

    @staticmethod
    def _to_list_item(s: Dict, summary_len: int = 250, reason: Optional[str] = None) -> SchemeListItem:
        slug = s["_clean_slug"]
        desc = s.get("Description", "") or ""
        summary = desc[:summary_len] + ("..." if len(desc) > summary_len else "")
        return SchemeListItem(
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

        return [
            self._to_list_item(s, summary_len=200, reason=reason)
            for _, s, reason in candidates[:profile.limit]
        ]


scheme_service = SchemeCatalogService()

