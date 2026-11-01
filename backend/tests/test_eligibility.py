import pytest
from backend.app.services.eligibility_engine import eligibility_engine
from backend.app.schemas.eligibility import EligibilityStatusEnum


def test_national_scholarship_eligible():
    """Student with OBC category and family income under ₹2.5L qualifies."""
    profile = {
        "annual_family_income": 200000.0,
        "caste_category": "OBC",
        "education_level": "Undergraduate",
        "student_status": "Student"
    }
    result = eligibility_engine.evaluate("national-scholarship-post-matric", profile)
    assert result.status == EligibilityStatusEnum.POTENTIALLY_ELIGIBLE
    assert len(result.matched_rules) >= 3
    assert len(result.failed_rules) == 0
    assert len(result.missing_fields) == 0


def test_national_scholarship_income_exceeded():
    """Student with income exceeding ₹2.5L fails eligibility deterministically."""
    profile = {
        "annual_family_income": 350000.0,
        "caste_category": "OBC",
        "education_level": "Undergraduate",
        "student_status": "Student"
    }
    result = eligibility_engine.evaluate("national-scholarship-post-matric", profile)
    assert result.status == EligibilityStatusEnum.NOT_ELIGIBLE
    assert any(r.rule_key == "annual_family_income" and r.passed is False for r in result.failed_rules)


def test_national_scholarship_caste_mismatch():
    """General category student applying for SC/ST/OBC/Minority scheme fails category rule."""
    profile = {
        "annual_family_income": 150000.0,
        "caste_category": "General",
        "education_level": "Undergraduate",
        "student_status": "Student"
    }
    result = eligibility_engine.evaluate("national-scholarship-post-matric", profile)
    assert result.status == EligibilityStatusEnum.NOT_ELIGIBLE
    assert any(r.rule_key == "caste_category" and r.passed is False for r in result.failed_rules)


def test_national_scholarship_missing_income():
    """When income is unknown, system returns needs_information instead of guessing."""
    profile = {
        "annual_family_income": None,
        "caste_category": "SC",
        "education_level": "Undergraduate",
        "student_status": "Student"
    }
    result = eligibility_engine.evaluate("national-scholarship-post-matric", profile)
    assert result.status == EligibilityStatusEnum.NEEDS_INFORMATION
    assert "annual_family_income" in result.missing_fields


def test_farmer_pm_kisan_eligible():
    """Farmer with agricultural land ownership qualifies for PM-KISAN."""
    profile = {
        "occupation": "Farmer (Cultivator / Landowner)",
        "is_landowner": True,
        "land_holding_acres": 2.5,
        "is_bank_aadhaar_seeded": True
    }
    result = eligibility_engine.evaluate("pm-kisan", profile)
    assert result.status == EligibilityStatusEnum.POTENTIALLY_ELIGIBLE
    assert any(r.rule_key == "is_landowner" and r.passed is True for r in result.matched_rules)


def test_citizen_ayushman_bharat_eligible():
    """Citizen with BPL ration card qualifies for Ayushman Bharat health cover."""
    profile = {
        "ration_card_type": "BPL / Priority Household (PHH)",
        "annual_family_income": 180000.0
    }
    result = eligibility_engine.evaluate("ayushman-bharat-pmjay", profile)
    assert result.status == EligibilityStatusEnum.POTENTIALLY_ELIGIBLE


