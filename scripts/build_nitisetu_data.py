import json
import os
import re
from collections import defaultdict

def ensure_dirs():
    dirs = [
        'data/schemes/by_category',
        'data/eligibility_rules',
        'data/document_requirements',
        'data/application_forms_and_workflows',
        'data/official_policy_guidelines',
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def build_category_datasets():
    print("Building category-wise datasets from myscheme JSON...")
    with open('data/schemes/myscheme_central_state_schemes.json', 'r', encoding='utf-8') as f:
        schemes = json.load(f)

    categories = {
        'agriculture_and_farmers': ['agriculture', 'farmer', 'kisan', 'crop', 'irrigation', 'fertilizer', 'livestock', 'dairy', 'fisheries', 'horticulture'],
        'education_and_scholarships': ['student', 'scholarship', 'education', 'school', 'college', 'fellowship', 'university', 'tuition', 'stipend', 'hostel'],
        'healthcare_and_wellness': ['health', 'medical', 'hospital', 'patient', 'treatment', 'disease', 'maternity', 'ayushman', 'medicine', 'disability'],
        'housing_and_urban_rural': ['housing', 'house', 'awas', 'shelter', 'urban', 'rural', 'slum', 'sanitation', 'electrification', 'toilet'],
        'women_and_child_development': ['women', 'girl', 'child', 'mother', 'widow', 'maternity', 'daughter', 'female', 'kanya', 'mahila'],
        'social_justice_and_pensions': ['pension', 'senior citizen', 'old age', 'scheduled caste', 'scheduled tribe', 'sc/st', 'obc', 'vulnerable', 'destitute', 'differently abled', 'handicapped', 'pwd'],
        'business_msme_and_loans': ['msme', 'business', 'entrepreneur', 'loan', 'credit', 'mudra', 'startup', 'vendor', 'subsidy', 'capital', 'artisan', 'craftsman'],
        'skills_and_employment': ['employment', 'skill', 'training', 'unemployed', 'job', 'apprentice', 'vocational', 'livelihood', 'worker', 'labour']
    }

    categorized_schemes = defaultdict(list)
    scheme_docs_matrix = {}

    doc_keywords = {
        'aadhaar_card': ['aadhaar', 'aadhar', 'uid'],
        'passport_size_photo': ['photograph', 'photo', 'passport size'],
        'bank_passbook_account': ['bank account', 'passbook', 'bank details', 'ifsc'],
        'income_certificate': ['income certificate', 'income proof', 'salary certificate'],
        'caste_category_certificate': ['caste certificate', 'community certificate', 'tribe certificate', 'sc/st', 'obc certificate'],
        'residence_domicile_certificate': ['domicile', 'residence certificate', 'nativity certificate', 'residential proof', 'address proof'],
        'ration_card_bpl': ['ration card', 'bpl card', 'aay card', 'food security card'],
        'birth_certificate_age_proof': ['birth certificate', 'age proof', 'dob certificate'],
        'pan_card': ['pan card', 'pan'],
        'educational_marksheets': ['marksheet', 'educational qualification', 'degree', '10th certificate', '12th certificate'],
        'voter_id_card': ['voter id', 'epic'],
        'disability_certificate_udid': ['disability certificate', 'handicapped certificate', 'udid'],
        'death_certificate': ['death certificate'],
        'bonafide_student_certificate': ['bonafide', 'enrollment certificate', 'college id', 'school certificate'],
        'land_records_khasra_ror': ['land record', 'khasra', 'khatauni', 'ror', 'patta', 'land document', 'land holding']
    }

    for s in schemes:
        slug = s.get('Scheme Slug') or s.get('Scheme Name', '').lower().replace(' ', '-')
        text_blob = f"{s.get('Scheme Name', '')} {s.get('Tags / Categories', '')} {s.get('Description', '')} {s.get('Eligibility Criteria', '')}".lower()

        # Categorize
        for cat_name, keywords in categories.items():
            if any(k in text_blob for k in keywords):
                categorized_schemes[cat_name].append({
                    'name': s.get('Scheme Name'),
                    'slug': slug,
                    'level': s.get('Level'),
                    'state_or_ministry': s.get('State / UT / Ministry'),
                    'mode': s.get('Application Mode'),
                    'brief_description': (s.get('Description') or '')[:300] + '...',
                    'benefits': (s.get('Benefits') or '')[:300] + '...',
                    'eligibility': (s.get('Eligibility Criteria') or '')[:300] + '...',
                    'official_url': s.get('Official Link') or s.get('MyScheme URL')
                })

        # Document Matrix
        docs_text = (s.get('Documents Required') or '').lower()
        required_docs = []
        for doc_key, kws in doc_keywords.items():
            if any(kw in docs_text for kw in kws):
                required_docs.append(doc_key)

        scheme_docs_matrix[slug] = {
            'scheme_name': s.get('Scheme Name'),
            'level': s.get('Level'),
            'state_or_ministry': s.get('State / UT / Ministry'),
            'application_mode': s.get('Application Mode'),
            'raw_documents_required': s.get('Documents Required'),
            'detected_document_tags': required_docs
        }

    # Save categories
    for cat_name, items in categorized_schemes.items():
        cat_file = f"data/schemes/by_category/{cat_name}.json"
        with open(cat_file, 'w', encoding='utf-8') as f:
            json.dump({
                'category': cat_name,
                'count': len(items),
                'schemes': items
            }, f, indent=2, ensure_ascii=False)
        print(f"  Saved {cat_file} ({len(items)} schemes)")

    # Save scheme-document matrix
    matrix_file = 'data/document_requirements/scheme_document_matrix.json'
    with open(matrix_file, 'w', encoding='utf-8') as f:
        json.dump(scheme_docs_matrix, f, indent=2, ensure_ascii=False)
    print(f"Saved {matrix_file} ({len(scheme_docs_matrix)} schemes indexed)")

def build_master_documents_catalog():
    print("Building master documents catalog...")
    catalog = {
        "metadata": {
            "title": "National Citizen Documents Catalog for Welfare & Schemes",
            "version": "1.0",
            "description": "Comprehensive authority, validity, and verification guide for government scheme documents."
        },
        "documents": [
            {
                "id": "aadhaar_card",
                "name": "Aadhaar Card (UIDAI)",
                "issuing_authority": "Unique Identification Authority of India (UIDAI), Ministry of Electronics & IT",
                "validity": "Lifetime (Requires periodic biometric update at ages 5 & 15)",
                "usage_frequency": "Required by >61% of all Indian Government schemes",
                "verification_method": "UIDAI OTP Authentication / Biometric / e-KYC XML / QR code verification",
                "key_fields": ["12-digit Aadhaar Number", "Full Name", "Date of Birth / Year of Birth", "Gender", "Address", "Linked Mobile Number", "Virtual ID (VID)"],
                "npci_seeding_requirement": "Crucial for Direct Benefit Transfer (DBT). Bank account must be seeded with NPCI Aadhaar payment bridge.",
                "official_portal": "https://myaadhaar.uidai.gov.in/"
            },
            {
                "id": "income_certificate",
                "name": "Income Certificate",
                "issuing_authority": "Revenue Department (Tehsildar / Sub-Divisional Magistrate / District Magistrate)",
                "validity": "Typically 1 Financial Year (April 1 to March 31)",
                "usage_frequency": "Required for all means-tested schemes (scholarships, housing, pensions, subsidies)",
                "verification_method": "State e-District portal certificate number verification / QR code scan",
                "key_fields": ["Application No / Certificate No", "Applicant Name", "Father/Husband Name", "Total Annual Family Income (INR)", "Village/Town", "Issue Date & Expiry", "Digital Signature of Tehsildar"],
                "income_brackets": [
                    {"bracket": "Antyodaya / Extremely Poor", "ceiling_inr": "< 50,000"},
                    {"bracket": "BPL (Below Poverty Line)", "ceiling_inr": "< 1,20,000 to 1,50,000 (State specific)"},
                    {"bracket": "Scholarship Threshold", "ceiling_inr": "< 2,50,000"},
                    {"bracket": "EWS (Economically Weaker Section)", "ceiling_inr": "< 8,00,000"}
                ],
                "official_portal": "State e-District / Edistrict.gov.in"
            },
            {
                "id": "caste_category_certificate",
                "name": "Caste / Community Certificate (SC / ST / OBC / EWS)",
                "issuing_authority": "Revenue Department / Competent Magistrate / SDO",
                "validity": "SC/ST: Lifetime; OBC-NCL (Non-Creamy Layer): 1 Financial Year; EWS: 1 Financial Year",
                "usage_frequency": "Required for affirmative action welfare schemes, affirmative scholarships, fee concessions",
                "verification_method": "e-District verification portal / Caste certificate tracking system",
                "key_fields": ["Certificate Number", "Applicant Name", "Father's Name", "Caste / Sub-caste / Tribe Name", "Constitutional Order Reference", "Non-Creamy Layer declaration (for OBC)", "Date of Issue"],
                "official_portal": "National Portal / State e-District Portals"
            },
            {
                "id": "residence_domicile_certificate",
                "name": "Domicile / Permanent Resident Certificate (PRC)",
                "issuing_authority": "District Magistrate / SDO / Tehsildar",
                "validity": "Lifetime (unless specified otherwise by State Gazette)",
                "usage_frequency": "Required for State-sponsored welfare schemes (over 1,500 State/UT schemes)",
                "verification_method": "State e-District portal barcode / certificate lookup",
                "key_fields": ["Certificate Number", "Resident Name", "Years of Continuous Residence in State", "Residential Address", "Village / Ward / Tehsil / District", "Digital Seal of Issuing Officer"],
                "official_portal": "State e-District Portals"
            },
            {
                "id": "bank_passbook_account",
                "name": "Bank Account Passbook / Statement (DBT-Enabled)",
                "issuing_authority": "Scheduled Commercial Banks / Regional Rural Banks / India Post Payments Bank (IPPB)",
                "validity": "Active account (Must not be dormant / inoperative)",
                "usage_frequency": "Mandatory for 100% of cash DBT subsidy & pension schemes",
                "verification_method": "Public Financial Management System (PFMS) penny drop / Account validation API",
                "key_fields": ["Account Holder Name (must match Aadhaar spelling)", "Account Number", "IFSC Code", "Bank Name & Branch", "Aadhaar NPCI Mapping Status (Mapped/Unmapped)"],
                "official_portal": "https://pfms.nic.in/"
            },
            {
                "id": "land_records_khasra_ror",
                "name": "Land Records / Record of Rights (RoR / Khasra / Khatauni / Jamabandi)",
                "issuing_authority": "Department of Land Resources / Revenue Department",
                "validity": "Current revenue year / Latest mutation entry",
                "usage_frequency": "Mandatory for PM-KISAN, PMFBY (Crop Insurance), Kisan Credit Card (KCC), Agri-subsidies",
                "verification_method": "Bhoomi / Bhulekh / Banglarbhumi / MeeBhoomi / AnyRoR state land record APIs",
                "key_fields": ["Khata / Khewat Number", "Khasra / Survey Number", "Land Area (in Hectares / Acres / Bighas)", "Cultivable Area", "Owner / Co-sharer Name", "Land Classification (Irrigated / Unirrigated)"],
                "official_portal": "https://dilrmp.gov.in/ & State Bhulekh Portals"
            },
            {
                "id": "ration_card_bpl",
                "name": "Ration Card (NFSA / BPL / AAY)",
                "issuing_authority": "Department of Food & Public Distribution / State Food & Civil Supplies",
                "validity": "Valid as long as family fulfills NFSA quota / verified annually",
                "usage_frequency": "Required for PMAY Housing, Ayushman Bharat eligibility (SECC), Free Foodgrain (PMGKAY), State food subsidies",
                "verification_method": "Annavitran Portal / State NFSA PDS Portal API / RCMS lookup",
                "key_fields": ["Ration Card Number (12 or 10 digits)", "Card Type (AAY - Antyodaya, PHH - Priority Household, Non-NFSA)", "Head of Family Name", "Family Members List with Aadhaar UID", "FPS (Fair Price Shop) Code"],
                "official_portal": "https://nfsa.gov.in/"
            },
            {
                "id": "disability_certificate_udid",
                "name": "Unique Disability ID (UDID) / Disability Certificate",
                "issuing_authority": "Department of Empowerment of Persons with Disabilities, Ministry of Social Justice & District Medical Board",
                "validity": "Permanent (for non-progressive disabilities) or Temporary (with specified re-assessment date)",
                "usage_frequency": "Required for Divyangjan pensions, assistive aids (ADIP), reserved scholarships, travel concessions",
                "verification_method": "Swavlamban Card Portal verification API",
                "key_fields": ["UDID Number", "Name of PwD", "Disability Type (Locomotor, Visual, Hearing, Intellectual, etc.)", "Percentage of Disability (Minimum 40% required for government benefits)", "Issuing Medical Hospital & CMO Signature"],
                "official_portal": "https://www.swavlambancard.gov.in/"
            },
            {
                "id": "educational_marksheets",
                "name": "Educational Marksheets & Certificates (10th, 12th, Degree, Bonafide)",
                "issuing_authority": "State School Boards / CBSE / ICSE / Recognized Universities / DigiLocker",
                "validity": "Permanent",
                "usage_frequency": "Required for all student scholarships (National Scholarship Portal, Post-Matric, State Merit Schemes)",
                "verification_method": "DigiLocker NAD (National Academic Depository) / Roll Number verification API",
                "key_fields": ["Board / University Roll Number", "Year of Passing", "Marks Obtained & Maximum Marks", "Percentage / CGPA", "Institution Name", "AISHE / UDISE Code of Institution"],
                "official_portal": "https://www.digilocker.gov.in/ & https://scholarships.gov.in/"
            }
        ]
    }
    with open('data/document_requirements/master_documents_catalog.json', 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    print("Saved data/document_requirements/master_documents_catalog.json")

def build_eligibility_rules_engine():
    print("Building eligibility rules engine and citizen profile schema...")
    
    # 1. Citizen Profile Schema
    profile_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CitizenProfile",
        "type": "object",
        "required": ["full_name", "age", "gender", "state_residence", "annual_household_income", "caste_category", "occupation"],
        "properties": {
            "full_name": {"type": "string", "description": "Citizen full legal name matching Aadhaar"},
            "age": {"type": "integer", "minimum": 0, "maximum": 120, "description": "Age in completed years"},
            "gender": {"type": "string", "enum": ["Male", "Female", "Transgender", "Other"]},
            "marital_status": {"type": "string", "enum": ["Single", "Married", "Widowed", "Divorced", "Deserted"]},
            "state_residence": {"type": "string", "description": "State or Union Territory of permanent residence"},
            "district": {"type": "string", "description": "District within the State"},
            "domicile_status": {"type": "boolean", "description": "Whether citizen holds official State Domicile / PRC"},
            "area_type": {"type": "string", "enum": ["Rural", "Urban"]},
            "annual_household_income": {"type": "number", "minimum": 0, "description": "Total family annual income in INR from all sources"},
            "caste_category": {"type": "string", "enum": ["General", "OBC", "SC", "ST", "EWS", "Minority"]},
            "is_minority_community": {"type": "boolean", "description": "Muslim, Christian, Sikh, Buddhist, Jain, Parsi"},
            "occupation": {
                "type": "string",
                "enum": [
                    "Farmer (Cultivator / Landowner)",
                    "Agricultural Labourer",
                    "Student",
                    "Traditional Artisan / Craftsman",
                    "Street Vendor / Micro-vendor",
                    "Construction Worker / Daily Wager",
                    "Salaried (Private / Formal)",
                    "Government Employee",
                    "Self-Employed / MSME Owner",
                    "Unemployed",
                    "Homemaker",
                    "Retired / Senior Citizen"
                ]
            },
            "is_landowner": {"type": "boolean", "description": "Owns cultivable agricultural land"},
            "land_holding_acres": {"type": "number", "minimum": 0, "description": "Total landholding in acres"},
            "is_pwd": {"type": "boolean", "description": "Person with Benchmark Disability (>=40%)"},
            "pwd_percentage": {"type": "integer", "minimum": 0, "maximum": 100},
            "ration_card_type": {"type": "string", "enum": ["None", "Antyodaya (AAY)", "BPL / Priority Household (PHH)", "APL / Non-NFSA"]},
            "highest_qualification": {"type": "string", "enum": ["Illiterate", "Below 10th", "10th Passed", "12th Passed", "Graduate", "Postgraduate", "Vocational / ITI / Diploma"]},
            "has_bank_account": {"type": "boolean"},
            "is_bank_aadhaar_seeded": {"type": "boolean", "description": "Aadhaar seeded in NPCI mapper for Direct Benefit Transfer"},
            "documents_ready": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of verified document IDs currently possessed by the citizen"
            }
        }
    }
    with open('data/eligibility_rules/citizen_profile_schema.json', 'w', encoding='utf-8') as f:
        json.dump(profile_schema, f, indent=2)

    # 2. Eligibility Rules Engine
    rules_engine = {
        "metadata": {
            "title": "NitiSetu Dynamic Scheme Matching Rules",
            "version": "1.0",
            "rule_evaluation_logic": "All specified conditions for a scheme must evaluate to TRUE for citizen eligibility."
        },
        "flagship_scheme_rules": [
            {
                "scheme_slug": "pm-kisan",
                "scheme_name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
                "category": "Agriculture",
                "benefit_summary": "₹6,000 per year paid in three 4-monthly installments of ₹2,000 directly via DBT.",
                "eligibility_conditions": {
                    "is_landowner": True,
                    "occupation_in": ["Farmer (Cultivator / Landowner)"],
                    "is_bank_aadhaar_seeded": True
                },
                "exclusions": [
                    "Institutional landholders",
                    "Farmer families where any member holds or held constitutional posts",
                    "Former and present Ministers, MPs, MLAs, MLCs, Mayors, District Panchayat Chairpersons",
                    "Serving or retired officers and employees of Central/State Govt Ministries, Departments, PSEs, Attached offices",
                    "All superannuated/retired pensioners whose monthly pension is ₹10,000 or more (excluding MTS/Class IV/Group D)",
                    "All persons who paid Income Tax in last assessment year",
                    "Professionals like Doctors, Engineers, Lawyers, Chartered Accountants, Architects"
                ],
                "mandatory_documents": ["aadhaar_card", "land_records_khasra_ror", "bank_passbook_account"]
            },
            {
                "scheme_slug": "ayushman-bharat-pmjay",
                "scheme_name": "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana (PM-JAY)",
                "category": "Healthcare",
                "benefit_summary": "Cashless health insurance cover of ₹5,00,000 per eligible family per year for secondary and tertiary hospitalization.",
                "eligibility_conditions": {
                    "ration_card_type_in": ["Antyodaya (AAY)", "BPL / Priority Household (PHH)"],
                    "annual_household_income_max": 250000
                },
                "exclusions": [
                    "Households owning motorized 2/3/4-wheeler or mechanized fishing boat",
                    "Households possessing Kisan Credit Card with credit limit of ₹50,000 or more",
                    "Household with government employees or income tax payers",
                    "Households with pucca houses with more than 3 rooms"
                ],
                "mandatory_documents": ["aadhaar_card", "ration_card_bpl"]
            },
            {
                "scheme_slug": "national-scholarship-post-matric",
                "scheme_name": "Post-Matric Scholarship Scheme for SC/ST/OBC/Minorities",
                "category": "Education",
                "benefit_summary": "Full tuition fee reimbursement + monthly maintenance allowance (up to ₹1,200/month) for higher education.",
                "eligibility_conditions": {
                    "occupation_in": ["Student"],
                    "caste_category_in": ["SC", "ST", "OBC", "Minority", "EWS"],
                    "highest_qualification_in": ["10th Passed", "12th Passed", "Graduate"],
                    "annual_household_income_max": 250000
                },
                "mandatory_documents": ["aadhaar_card", "income_certificate", "caste_category_certificate", "educational_marksheets", "bonafide_student_certificate", "bank_passbook_account"]
            },
            {
                "scheme_slug": "pm-vishwakarma",
                "scheme_name": "PM Vishwakarma Scheme",
                "category": "Livelihood & Crafts",
                "benefit_summary": "Free PM Vishwakarma Certificate & ID card, 5-7 days basic skill training with ₹500/day stipend, ₹15,000 e-voucher toolkit incentive, collateral-free credit up to ₹3,00,000 at concessional 5% interest.",
                "eligibility_conditions": {
                    "age_min": 18,
                    "occupation_in": ["Traditional Artisan / Craftsman"],
                    "traditional_trades_eligible": [
                        "Carpenter (Suthar)", "Boat Maker", "Armourer", "Blacksmith (Lohar)", "Hammer and Tool Kit Maker",
                        "Locksmith", "Sculptor (Moortikar/Stone carver)", "Stone breaker", "Goldsmith (Sonar)", "Potter (Kumhaar)",
                        "Cobbler (Charmakar/Shoemaker)", "Mason (Rajmistri)", "Basket/Mat/Broom Maker/Coir Weaver",
                        "Doll & Toy Maker (Traditional)", "Barber (Naai)", "Garland maker (Malakaar)", "Washerman (Dhobi)",
                        "Tailor (Darzi)", "Fishing Net Maker"
                    ]
                },
                "exclusions": ["Persons who have availed loans under PMEGP, PM SVANidhi, or Mudra in past 5 years and have outstanding balance", "Only one member per family eligible"],
                "mandatory_documents": ["aadhaar_card", "bank_passbook_account", "passport_size_photo"]
            },
            {
                "scheme_slug": "pm-svanidhi",
                "scheme_name": "PM Street Vendor's AtmaNirbhar Nidhi (PM SVANidhi)",
                "category": "Micro-credit / Livelihood",
                "benefit_summary": "Collateral-free working capital loan: 1st tranche ₹10,000 (1 year), 2nd tranche ₹20,000, 3rd tranche ₹50,000. 7% interest subsidy on timely repayment, cashback up to ₹1,200/year on digital transactions.",
                "eligibility_conditions": {
                    "area_type": "Urban",
                    "occupation_in": ["Street Vendor / Micro-vendor"]
                },
                "mandatory_documents": ["aadhaar_card", "voter_id_card", "bank_passbook_account"]
            },
            {
                "scheme_slug": "pm-surya-ghar-muft-bijli",
                "scheme_name": "PM Surya Ghar: Muft Bijli Yojana",
                "category": "Clean Energy / Subsidy",
                "benefit_summary": "Direct capital subsidy for residential rooftop solar: ₹30,000 for 1 kW, ₹60,000 for 2 kW, ₹78,000 for 3 kW and above. Provides up to 300 units free electricity per month.",
                "eligibility_conditions": {
                    "has_electricity_connection": True,
                    "owns_roof_space": True
                },
                "mandatory_documents": ["aadhaar_card", "bank_passbook_account", "electricity_bill"]
            },
            {
                "scheme_slug": "sukanya-samriddhi-yojana",
                "scheme_name": "Sukanya Samriddhi Yojana (SSY)",
                "category": "Women & Child",
                "benefit_summary": "High government interest rate (8.2% p.a.), exempt under 80C, tax-free interest and maturity corpus for daughter's education and marriage.",
                "eligibility_conditions": {
                    "gender": "Female",
                    "age_max": 10
                },
                "mandatory_documents": ["birth_certificate_age_proof", "aadhaar_card", "passport_size_photo"]
            }
        ]
    }
    with open('data/eligibility_rules/eligibility_rule_engine.json', 'w', encoding='utf-8') as f:
        json.dump(rules_engine, f, indent=2, ensure_ascii=False)
    print("Saved data/eligibility_rules/eligibility_rule_engine.json")

def build_application_workflows():
    print("Building detailed government application workflows and form schemas...")
    workflows = {
        "pm_kisan_workflow": {
            "scheme_name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
            "official_portal": "https://pmkisan.gov.in/",
            "application_mode": "Online (Self-Registration) or CSC (Common Service Centre)",
            "target_beneficiary": "Small & Marginal Farmers owning cultivable land",
            "financial_benefit": "₹6,000 annually in 3 installments of ₹2,000 directly to Aadhaar-seeded bank account",
            "prerequisites": [
                "Aadhaar Number linked with active mobile number for OTP",
                "Cultivable land record (Khasra / Khatauni) in applicant's name",
                "DBT-enabled Bank Account seeded with NPCI"
            ],
            "application_steps": [
                {
                    "step_number": 1,
                    "step_name": "Farmer Registration & Aadhaar Authentication",
                    "portal_action": "Navigate to Farmers Corner -> 'New Farmer Registration'",
                    "input_fields": [
                        {"name": "farmer_type", "type": "select", "options": ["Rural Farmer Registration", "Urban Farmer Registration"], "mandatory": True},
                        {"name": "aadhaar_number", "type": "string", "pattern": "^[2-9]{1}[0-9]{11}$", "description": "12 digit UID", "mandatory": True},
                        {"name": "mobile_number", "type": "string", "pattern": "^[6-9][0-9]{9}$", "description": "Aadhaar linked 10-digit mobile", "mandatory": True},
                        {"name": "state", "type": "select", "mandatory": True},
                        {"name": "captcha", "type": "string", "mandatory": True}
                    ],
                    "verification": "Aadhaar OTP is dispatched to citizen's mobile. Citizen enters 6-digit OTP to verify identity."
                },
                {
                    "step_number": 2,
                    "step_name": "Personal & Demographic Details",
                    "portal_action": "Pre-filled from UIDAI database with required manual additions",
                    "input_fields": [
                        {"name": "district", "type": "select", "mandatory": True},
                        {"name": "sub_district_tehsil", "type": "select", "mandatory": True},
                        {"name": "block", "type": "select", "mandatory": True},
                        {"name": "village", "type": "select", "mandatory": True},
                        {"name": "farmer_category", "type": "select", "options": ["General", "OBC", "SC", "ST"], "mandatory": True},
                        {"name": "farmer_type", "type": "select", "options": ["Small (1-2 Ha)", "Marginal (<1 Ha)", "Others (>2 Ha)"], "mandatory": True},
                        {"name": "pin_code", "type": "string", "pattern": "^[1-9][0-9]{5}$", "mandatory": True}
                    ]
                },
                {
                    "step_number": 3,
                    "step_name": "Land Record Seeding (Bhoomi / Bhulekh Details)",
                    "portal_action": "Enter revenue land ownership details",
                    "input_fields": [
                        {"name": "ownership_type", "type": "radio", "options": ["Single", "Joint"], "mandatory": True},
                        {"name": "survey_khata_number", "type": "string", "description": "Khata/Khewat number from Land Record", "mandatory": True},
                        {"name": "khasra_dag_number", "type": "string", "description": "Khasra / Plot Number", "mandatory": True},
                        {"name": "area_in_hectare", "type": "float", "mandatory": True},
                        {"name": "land_transfer_status", "type": "select", "options": ["Before 01-02-2019", "After 01-02-2019"], "mandatory": True},
                        {"name": "land_transfer_details", "type": "select", "options": ["Death of Husband", "Death of Father", "Ancestral", "Purchase", "Gift", "Pattadar"], "mandatory": True},
                        {"name": "land_record_pdf", "type": "file", "allowed_format": "PDF", "max_size_kb": 200, "mandatory": True}
                    ]
                },
                {
                    "step_number": 4,
                    "step_name": "e-KYC & Final Declaration",
                    "portal_action": "Undertaking of exclusion criteria and biometric/OTP eKYC",
                    "input_fields": [
                        {"name": "income_tax_exclusion_declaration", "type": "checkbox", "mandatory": True},
                        {"name": "constitutional_post_exclusion_declaration", "type": "checkbox", "mandatory": True}
                    ],
                    "output_artifact": "Farmer Application Reference ID (e.g. UP123456789) generated for status tracking."
                }
            ],
            "approval_and_redressal_flow": {
                "level_1": "Verification by Patwari / Lekhpal (Village level)",
                "level_2": "Sub-Divisional Nodal Officer (Tehsildar / SDO)",
                "level_3": "District Agriculture Officer (DAO)",
                "level_4": "State Nodal Officer -> PFMS validation -> Installment Release",
                "tracking_url": "https://pmkisan.gov.in/BeneficiaryStatus_New.aspx",
                "helpline": "155261 / 011-24300606"
            }
        },
        "ayushman_bharat_pmjay_workflow": {
            "scheme_name": "Ayushman Bharat PM-JAY (Ayushman Card Generation)",
            "official_portal": "https://beneficiary.nha.gov.in/",
            "application_mode": "Online (Beneficiary Portal / Ayushman App) or Empanelled Hospital / CSC",
            "benefit_summary": "₹5,00,000 free cashless hospital treatment per family per year in empanelled hospitals.",
            "application_steps": [
                {
                    "step_number": 1,
                    "step_name": "Beneficiary Identification & Search",
                    "portal_action": "Log in with Mobile OTP as 'Beneficiary'",
                    "search_criteria": [
                        {"field": "State", "type": "select"},
                        {"field": "Scheme", "type": "select", "options": ["PMJAY", "State Healthcare Schemes"]},
                        {"field": "Search By", "type": "select", "options": ["Aadhaar Number", "Family ID / Ration Card Number", "PMJAY ID", "Location (Rural/Urban)"]}
                    ]
                },
                {
                    "step_number": 2,
                    "step_name": "e-KYC Authentication",
                    "portal_action": "If member status is 'Action Required', perform e-KYC",
                    "modes": ["Aadhaar OTP", "Fingerprint Biometric", "Iris Scan", "Face Authentication (via Ayushman App)"]
                },
                {
                    "step_number": 3,
                    "step_name": "Live Photograph Capture & Matching",
                    "portal_action": "Capture live photo. System verifies match score (>80%) against Aadhaar photo."
                },
                {
                    "step_number": 4,
                    "step_name": "Card Approval & Download",
                    "portal_action": "Auto-approved or approved by NHA within 24 hours. Download official PVC Ayushman Golden Card PDF."
                }
            ],
            "hospital_treatment_workflow": {
                "step_1": "Visit any empanelled public or private hospital across India",
                "step_2": "Approach 'Ayushman Mitra' help desk with Ayushman Card / Aadhaar",
                "step_3": "Pre-authorization request generated by hospital doctor",
                "step_4": "Cashless admission, diagnostics, surgeries, and medicines up to ₹5 Lakh",
                "helpline": "14555 / 1800 111 565"
            }
        },
        "national_scholarship_portal_workflow": {
            "scheme_name": "National Scholarship Portal (NSP - scholarships.gov.in)",
            "official_portal": "https://scholarships.gov.in/",
            "target_beneficiaries": "Pre-Matric, Post-Matric, Top-Class, and Merit-cum-Means students from minority, SC, ST, OBC, and EWS backgrounds.",
            "application_steps": [
                {
                    "step_number": 1,
                    "step_name": "One Time Registration (OTR)",
                    "portal_action": "Generate unique 14-digit OTR number via Aadhaar / Face Auth on NSP OTR App",
                    "input_fields": ["Aadhaar Number", "Active Mobile Number", "Parent/Guardian Aadhaar (for minors)"]
                },
                {
                    "step_number": 2,
                    "step_name": "Student Profile & Academic Form Filling",
                    "portal_action": "Log in with OTR and fill application form",
                    "input_fields": [
                        {"name": "domicile_state", "type": "select", "mandatory": True},
                        {"name": "scholarship_category", "type": "select", "options": ["Pre-Matric (Class 1-10)", "Post-Matric / Top-Class / MCM (Class 11, 12, UG, PG, Ph.D.)"], "mandatory": True},
                        {"name": "institution_state_district", "type": "select", "mandatory": True},
                        {"name": "institution_name", "type": "select", "description": "Must have valid AISHE / UDISE code", "mandatory": True},
                        {"name": "present_class_course", "type": "select", "mandatory": True},
                        {"name": "present_class_year", "type": "select", "mandatory": True},
                        {"name": "mode_of_study", "type": "radio", "options": ["Regular / Full Time", "Distance / Part Time"], "mandatory": True},
                        {"name": "previous_passing_percentage", "type": "float", "mandatory": True},
                        {"name": "family_annual_income", "type": "number", "mandatory": True},
                        {"name": "day_scholar_or_hosteller", "type": "radio", "options": ["Day Scholar", "Hosteller"], "mandatory": True}
                    ]
                },
                {
                    "step_number": 3,
                    "step_name": "Scheme Selection & Document Upload",
                    "portal_action": "System dynamically presents eligible central/state schemes based on student profile",
                    "documents_to_upload": [
                        "Bonafide Student Certificate signed by School Principal / Dean",
                        "Income Certificate from Competent Authority",
                        "Caste / Community Certificate",
                        "Self-attested previous year marksheet",
                        "Fee receipt of current academic course",
                        "Bank Passbook copy (Account must be in student's name & Aadhaar-seeded)"
                    ]
                },
                {
                    "step_number": 4,
                    "step_name": "Institutional & Nodal Officer Verification (L1 & L2)",
                    "workflow": [
                        "L1 Verification: Institute Nodal Officer (INO) verifies student bonafide & fee details",
                        "L2 Verification: District Nodal Officer (DNO) / State Nodal Officer (SNO) verifies income and caste genuineness",
                        "PFMS Merit List Generation & Direct Benefit Transfer to bank account"
                    ]
                }
            ],
            "tracking_url": "https://scholarships.gov.in/portal/loginPage",
            "helpline": "0120 - 6619540"
        },
        "pm_vishwakarma_workflow": {
            "scheme_name": "PM Vishwakarma Scheme",
            "official_portal": "https://pmvishwakarma.gov.in/",
            "application_mode": "CSC (Common Services Centre) Assisted Registration with Biometric Auth",
            "eligible_trades": ["Carpenter", "Blacksmith", "Goldsmith", "Potter", "Sculptor", "Cobbler", "Mason", "Basket Maker", "Doll Maker", "Barber", "Garland maker", "Washerman", "Tailor", "Fishing Net Maker", "Locksmith", "Tool Kit Maker", "Armourer", "Boat Maker"],
            "application_steps": [
                {
                    "step_number": 1,
                    "step_name": "Mobile & Aadhaar Verification",
                    "action": "Artisan visits nearest CSC. Enters Aadhaar & mobile number. Completes biometric fingerprint scan."
                },
                {
                    "step_number": 2,
                    "step_name": "Artisan Profile & Trade Details",
                    "action": "Select trade from 18 traditional professions. Enter family details and address."
                },
                {
                    "step_number": 3,
                    "step_name": "Bank Account & Credit Support Preference",
                    "action": "Enter bank account details for stipend & ₹15,000 tool kit incentive. Choose whether loan is requested (Tranche 1: ₹1 Lakh @ 5%)."
                },
                {
                    "step_number": 4,
                    "step_name": "Three-Tier Verification Process",
                    "workflow": [
                        "Tier 1: Gram Panchayat Head / Ward Member verification of trade practice",
                        "Tier 2: District Implementation Committee (headed by Collector / MSME DFO)",
                        "Tier 3: National Steering Committee approval -> PM Vishwakarma Digital Certificate & ID Card issued"
                    ]
                }
            ],
            "benefits_disbursement": {
                "training": "5-7 days basic training with ₹500/day stipend",
                "toolkit": "₹15,000 e-voucher via digital payment / UPI for modern tools",
                "loan": "Up to ₹3,00,000 collateral-free loan at 5% interest (Subsidized by GoI up to 8%)"
            }
        }
    }

    for wf_name, wf_data in workflows.items():
        wf_file = f"data/application_forms_and_workflows/{wf_name}.json"
        with open(wf_file, 'w', encoding='utf-8') as f:
            json.dump(wf_data, f, indent=2, ensure_ascii=False)
        print(f"Saved {wf_file}")

def build_official_guidelines_markdown():
    print("Writing authentic official policy guidelines summaries...")
    guidelines = {
        "pm_kisan_operational_guidelines.md": """# Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) - Official Operational Guidelines

**Issuing Authority**: Department of Agriculture and Farmers Welfare, Ministry of Agriculture & Farmers Welfare, Government of India  
**Official Portal**: [pmkisan.gov.in](https://pmkisan.gov.in/)

## 1. Scheme Objective
PM-KISAN is a Central Sector Scheme launched with 100% funding from the Government of India. It aims to supplement the financial needs of all landholding farmer families in procuring various inputs to ensure proper crop health and appropriate yields, commensurate with the anticipated farm income at the end of each crop cycle.

## 2. Benefits & Financial Norms
- **Quantum of Assistance**: ₹6,000 per year per farmer family.
- **Installment Frequency**: Paid in three equal installments of ₹2,000 every 4 months:
  - Period 1: April to July
  - Period 2: August to November
  - Period 3: December to March
- **Disbursement Mechanism**: Direct Benefit Transfer (DBT) directly into the Aadhaar-seeded bank account of the beneficiary via PFMS (Public Financial Management System).

## 3. Definition of Beneficiary Family
A 'farmer family' is defined as: **Husband, wife, and minor children** who jointly own cultivable land as per land records of the concerned State/UT.

## 4. Exclusion Criteria (Ineligible Categories)
The following categories of beneficiaries of higher economic status are **NOT eligible**:
1. All Institutional Landholders.
2. Farmer families in which one or more of its members belong to following categories:
   - Former and present holders of constitutional posts.
   - Former and present Ministers/State Ministers, former/present MPs, MLAs, MLCs, Mayors of Municipal Corporations, Chairpersons of District Panchayats.
   - All serving or retired officers and employees of Central/State Government Ministries/Offices/Departments and their field units, Central or State PSEs and Attached offices/Autonomous Institutions as well as regular employees of Local Bodies (*Excluding Multi Tasking Staff / Class IV / Group D employees*).
   - All superannuated/retired pensioners whose monthly pension is ₹10,000/- or more (*Excluding MTS/Class IV/Group D*).
   - All persons who paid Income Tax in the last assessment year.
   - Professionals like Doctors, Engineers, Lawyers, Chartered Accountants, and Architects registered with Professional bodies.

## 5. Mandatory Verification & e-KYC
- Mandatory 100% Aadhaar seeding of bank accounts.
- Mandatory Land Record verification (Bhoomi / Bhulekh integration).
- Periodic e-KYC authentication via OTP, Biometric, or Face Authentication.
""",
        "ayushman_bharat_pmjay_guidelines.md": """# Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana (PM-JAY) - Official Guidelines

**Issuing Authority**: National Health Authority (NHA), Ministry of Health & Family Welfare, Government of India  
**Official Portal**: [nha.gov.in](https://nha.gov.in/) / [beneficiary.nha.gov.in](https://beneficiary.nha.gov.in/)

## 1. Scheme Overview
Ayushman Bharat PM-JAY is the world's largest government funded healthcare assurance scheme, targeting over 12 crore poor and vulnerable families (approximately 55 crore beneficiaries) corresponding to the bottom 40% of the Indian population based on SECC 2011 and State NFSA ration card data.

## 2. Key Benefits
- **Coverage**: ₹5,00,000 per family per year on a family floater basis for secondary and tertiary care hospitalization.
- **Portability**: Cashless and paperless treatment at all empanelled public and private hospitals across the country.
- **Pre-existing Conditions**: All pre-existing conditions are covered from day one.
- **Family Size**: No cap on family size, gender, or age of members.
- **Coverage Scope**: Covers up to 3 days of pre-hospitalization and 15 days of post-hospitalization expenses including medicines and diagnostic tests.

## 3. Beneficiary Identification (BIS)
- Beneficiaries identified through SECC (Socio-Economic Caste Census) deprivation criteria in rural areas and occupational criteria in urban areas, expanded through NFSA priority ration cards.
- **Ayushman Card**: Digital/PVC identity card containing unique PMJAY ID and ABHA (Ayushman Bharat Health Account) number.
""",
        "pm_vishwakarma_guidelines.md": """# PM Vishwakarma Scheme - Official Scheme Guidelines

**Issuing Authority**: Ministry of Micro, Small and Medium Enterprises (MoMSME), Government of India  
**Official Portal**: [pmvishwakarma.gov.in](https://pmvishwakarma.gov.in/)

## 1. Scheme Objectives
To provide end-to-end holistic support to traditional artisans and craftspeople (*Vishwakarmas*) working with their hands and tools, in scaling their enterprises, improving quality, integrating with value chains, and preserving cultural heritage.

## 2. Eligible 18 Traditional Trades
1. Carpenter (*Suthar*)
2. Boat Maker
3. Armourer
4. Blacksmith (*Lohar*)
5. Hammer and Tool Kit Maker
6. Locksmith
7. Sculptor (*Moortikar*, Stone carver, Stone breaker)
8. Goldsmith (*Sonar*)
9. Potter (*Kumhaar*)
10. Cobbler (*Charmakar*, Shoesmith/Footwear artisan)
11. Mason (*Rajmistri*)
12. Basket / Mat / Broom Maker / Coir Weaver
13. Doll & Toy Maker (*Traditional*)
14. Barber (*Naai*)
15. Garland maker (*Malakaar*)
16. Washerman (*Dhobi*)
17. Tailor (*Darzi*)
18. Fishing Net Maker

## 3. Core Support Components
- **Recognition**: PM Vishwakarma Certificate and ID Card.
- **Skill Upgradation**: Basic Training of 5-7 days and Advanced Training of 15 days, with stipend of ₹500 per day.
- **Toolkit Incentive**: ₹15,000 e-voucher/digital payment for purchasing modern equipment.
- **Credit Support**:
  - Tranche 1: Up to ₹1,00,000 (18-month tenure) collateral-free.
  - Tranche 2: Up to ₹2,00,000 (30-month tenure) for beneficiaries maintaining standard repayment.
  - Concessional Interest: Fixed at 5% p.a. (Interest subvention of 8% paid by Ministry).
- **Incentive for Digital Transactions**: ₹1 per transaction up to 100 transactions per month.
"""
    }

    for fname, content in guidelines.items():
        fpath = f"data/official_policy_guidelines/{fname}"
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content.strip() + '\n')
        print(f"Saved {fpath}")

if __name__ == "__main__":
    ensure_dirs()
    build_category_datasets()
    build_master_documents_catalog()
    build_eligibility_rules_engine()
    build_application_workflows()
    build_official_guidelines_markdown()
    print("\nNitiSetu authentic data pipeline executed successfully!")
