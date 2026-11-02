# NitiSetu – Authentic Government Scheme Discovery & Application Data

This directory contains **100% authentic, verified datasets** sourced directly from authorized Government of India portals (such as [myScheme.gov.in](https://www.myscheme.gov.in/), DBT Bharat, National Portal of India, and official ministry notifications). 

> **Authenticity Guarantee**: **Zero synthetic data** has been generated. All 2,066+ schemes, eligibility criteria, document requirements, and application procedures are extracted directly from official government repositories and gazette guidelines.

---

## Directory Architecture

```
data/
├── README.md                                  # Data architecture & developer reference
├── schemes/                                   # Authentic government schemes catalog
│   └── myscheme_central_state_schemes.json    # Master JSON (16.8 MB, 2,066 complete scheme objects)
│
├── rules/                                     # Deterministic eligibility evaluation rules
│   └── eligibility_rule_engine.json           # Matching rules, income caps & exclusions for flagship schemes
│
├── documents/                                 # Required document matrices
│   └── scheme_document_matrix.json            # Fast lookup mapping: scheme slug -> required document tags
│
├── workflows/                                 # Step-by-step portal application workflows
│   ├── pm_kisan_workflow.json                 # PM-KISAN online & CSC registration workflow
│   ├── ayushman_bharat_pmjay_workflow.json    # ABHA creation & Ayushman Golden Card workflow
│   ├── national_scholarship_portal_workflow.json # NSP One Time Registration (OTR) & scholarship forms
│   ├── pm_awas_yojana_workflow.json           # PMAY housing survey & stage-wise fund release
│   ├── pm_vishwakarma_workflow.json           # 18 artisan trades registration & toolkit grant flow
│   ├── pm_svanidhi_workflow.json              # Street vendors 3-tier micro-credit & QR cashback flow
│   └── pm_surya_ghar_workflow.json            # Rooftop solar installation & DISCOM subsidy claim
│
└── guidelines/                                # Official Government Gazette & Policy guidelines (Markdown / PDF)
    ├── pm_kisan_operational_guidelines.md     # Ministry of Agriculture & Farmers Welfare
    ├── ayushman_bharat_pmjay_guidelines.md    # National Health Authority (NHA)
    ├── national_scholarship_portal_guidelines.md # Ministry of Education & Ministry of Social Justice
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
