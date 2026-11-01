# NitiSetu – Authentic Government Scheme Discovery & Application Data

This directory contains **100% authentic, verified datasets** sourced directly from authorized Government of India portals (such as [myScheme.gov.in](https://www.myscheme.gov.in/), DBT Bharat, National Portal of India, and official ministry notifications). 

> **Authenticity Guarantee**: **Zero synthetic data** has been generated. All 2,066+ schemes, eligibility criteria, document requirements, and application procedures are extracted directly from official government repositories and gazette guidelines.

---

## Directory Architecture

```
data/
├── README.md                                  # This documentation & developer reference
├── schemes/
│   ├── myscheme_central_state_schemes.csv     # Master CSV (15.8 MB, 2,066 schemes, 16 attributes)
│   ├── myscheme_central_state_schemes.json    # Master JSON (16.8 MB, complete scheme objects)
│   ├── urbanmorph_schemes_master_registry.json# Reconciled Register (1.96 MB, 11,000+ schemes)
│   ├── scheme_sectors_classification.json     # Taxonomies & Ministry classification (2.2 MB)
│   └── by_category/                           # Category-filtered subsets for fast querying
│       ├── agriculture_and_farmers.json       # 390 schemes (PM-KISAN, PMFBY, KCC, etc.)
│       ├── education_and_scholarships.json    # 852 schemes (NSP, Post-Matric, fellowships)
│       ├── healthcare_and_wellness.json       # 643 schemes (Ayushman Bharat, Jan Aushadhi)
│       ├── housing_and_urban_rural.json       # 409 schemes (PMAY-G, PMAY-U, etc.)
│       ├── women_and_child_development.json   # 810 schemes (Sukanya Samriddhi, PMMVY, etc.)
│       ├── social_justice_and_pensions.json   # 711 schemes (NSAP, Disability & Widow pensions)
│       ├── business_msme_and_loans.json       # 647 schemes (PM Mudra, Vishwakarma, SVANidhi)
│       └── skills_and_employment.json         # 885 schemes (PMKVY, Rozgar Mela, Apprentice)
│
├── eligibility_rules/
│   ├── citizen_profile_schema.json            # JSON Schema for citizen profiling (Age, Income, Caste, etc.)
│   └── eligibility_rule_engine.json           # Matching rules, income caps & exclusions for flagship schemes
│
├── document_requirements/
│   ├── master_documents_catalog.json          # Complete registry of 15+ official citizen documents (UIDAI, RoR, etc.)
│   └── scheme_document_matrix.json            # Fast lookup mapping: scheme slug -> required document tags
│
├── application_forms_and_workflows/           # Step-by-step form schemas & UI walkthroughs
│   ├── pm_kisan_workflow.json                 # PM-KISAN online & CSC registration workflow
│   ├── ayushman_bharat_pmjay_workflow.json    # ABHA creation & Ayushman Golden Card workflow
│   ├── national_scholarship_portal_workflow.json # NSP One Time Registration (OTR) & scholarship forms
│   ├── pm_awas_yojana_workflow.json           # PMAY housing survey & stage-wise fund release
│   ├── pm_vishwakarma_workflow.json           # 18 artisan trades registration & toolkit grant flow
│   ├── pm_svanidhi_workflow.json              # Street vendors 3-tier micro-credit & QR cashback flow
│   └── pm_surya_ghar_workflow.json            # Rooftop solar installation & DISCOM subsidy claim
│
└── official_policy_guidelines/                # Gazette operational guidelines issued by ministries
    ├── pm_kisan_operational_guidelines.md     # Ministry of Agriculture & Farmers Welfare
    ├── ayushman_bharat_pmjay_guidelines.md    # National Health Authority (NHA)
    ├── pm_vishwakarma_guidelines.md           # Ministry of Micro, Small and Medium Enterprises
    ├── pm_surya_ghar_guidelines.md            # Ministry of New and Renewable Energy
    ├── pmay_housing_guidelines.md             # MoHUA & Ministry of Rural Development
    └── pm_svanidhi_guidelines.md              # Ministry of Housing and Urban Affairs
```

---

## 1. Master Schemes Dataset Schema (`schemes/`)

The master dataset `myscheme_central_state_schemes.csv` standardizes all 2,066 government schemes across 16 comprehensive columns:

| Column Header | Description | Example Value |
|---|---|---|
| `Scheme Name` | Official name of the scheme | `Pradhan Mantri Kisan Samman Nidhi` |
| `Scheme Slug` | Unique slug used in URLs & APIs | `pm-kisan` |
| `Level` | Central vs State Government | `Central Government` / `State / UT Government` |
| `State / UT / Ministry` | Specific Ministry or State | `Ministry of Agriculture and Farmers Welfare` |
| `Application Mode` | Mode of application submission | `Online`, `Offline`, or `Online & Offline` |
| `Tags / Categories` | Sectors and target groups | `Agriculture, Farmer, Financial Assistance, Subsidy` |
| `Description` | Official purpose and summary | *Detailed policy narrative* |
| `Eligibility Criteria` | Full eligibility guidelines | *Age, income, landholding, caste requirements* |
| `Eligibility (General)`| Quick eligibility criteria | *Key eligibility conditions* |
| `Exclusions / Ineligibility` | Disqualifying attributes | *Income tax payees, constitutional posts, etc.* |
| `Benefits` | Direct financial / in-kind benefits | `₹6,000 per year in 3 four-monthly installments` |
| `Application Process` | Step-by-step citizen walkthrough | *Portal registration, form fill, e-KYC steps* |
| `Documents Required` | Authentic required documentation | *Aadhaar, Land records, Bank Passbook, etc.* |
| `Frequently Asked Questions`| Official FAQs and answers | *Official Q&A clarification* |
| `Official Link` | Ministry / Department portal | `https://pmkisan.gov.in/` |
| `MyScheme URL` | National portal listing | `https://www.myscheme.gov.in/schemes/pm-kisan` |

---

## 2. Document Requirements & Readiness Catalog (`document_requirements/`)

Analyzed across all 2,066 authentic schemes, the top required official documents are:
1. **Aadhaar Card (UIDAI)**: 1,277 schemes (61.8%)
2. **Passport Size Photograph**: 1,119 schemes (54.2%)
3. **Bank Account Details / Passbook (DBT/NPCI enabled)**: 970 schemes (47.0%)
4. **Residence / Domicile Certificate**: 479 schemes (23.2%)
5. **Ration Card (NFSA / BPL / AAY)**: 450 schemes (21.8%)
6. **Caste / Category Certificate (SC/ST/OBC/EWS)**: 433 schemes (21.0%)
7. **Income Certificate (Revenue Authority)**: 430 schemes (20.8%)
8. **Birth Certificate / Age Proof**: 352 schemes (17.0%)
9. **PAN Card**: 346 schemes (16.7%)
10. **Educational Marksheets / Certificates**: 296 schemes (14.3%)
11. **Voter ID Card (EPIC)**: 272 schemes (13.2%)
12. **Unique Disability ID (UDID)**: 201 schemes (9.7%)
13. **Bonafide Student Certificate**: 123 schemes (6.0%)
14. **Land Records (RoR / Khasra / Khatauni)**: 70 schemes (3.4%)

The file `scheme_document_matrix.json` allows NitiSetu to immediately tell any citizen which documents they need based on the schemes they select.

---

## 3. Quickstart: Loading Data in NitiSetu Backend

### Python (Pandas / RAG):
```python
import pandas as pd
import json

# 1. Load full schemes dataframe
df = pd.read_csv("data/schemes/myscheme_central_state_schemes.csv")
print(f"Loaded {len(df)} schemes.")

# 2. Query schemes by category or keyword
farmer_schemes = df[df["Tags / Categories"].str.contains("Farmer|Agriculture", case=False, na=False)]
print(f"Farmer Schemes found: {len(farmer_schemes)}")

# 3. Load structured Document Matrix for automated checklist generation
with open("data/document_requirements/scheme_document_matrix.json", "r") as f:
    doc_matrix = json.load(f)

pm_kisan_docs = doc_matrix.get("pm-kisan")
print("PM-KISAN Required Documents:", pm_kisan_docs["detected_document_tags"])

# 4. Load Step-by-Step Application Workflow Schema
with open("data/application_forms_and_workflows/pm_kisan_workflow.json", "r") as f:
    workflow = json.load(f)
print("Application Steps Count:", len(workflow["application_steps"]))
```
