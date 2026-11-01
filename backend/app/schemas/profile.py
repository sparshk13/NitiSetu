from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ProfileBase(BaseModel):
    full_name: Optional[str] = Field(None, description="Full legal name of citizen matching official ID")
    age: Optional[int] = Field(None, description="Age in completed years")
    gender: Optional[str] = Field(None, description="Gender (Female, Male, Transgender, Other)")
    marital_status: Optional[str] = Field(None, description="Marital status (Single, Married, Widowed, Divorced)")
    state_code: Optional[str] = Field(None, description="State / UT of permanent residence")
    district: Optional[str] = Field(None, description="District within the State")
    area_type: Optional[str] = Field("Rural", description="Residential area: Rural or Urban")
    occupation: Optional[str] = Field(None, description="Primary occupation or citizen category")
    annual_family_income: Optional[float] = Field(None, description="Annual gross household income in INR")
    ration_card_type: Optional[str] = Field(None, description="Ration card classification (None, Antyodaya (AAY), BPL / Priority Household, APL)")
    caste_category: Optional[str] = Field(None, description="Social category: General, SC, ST, OBC, EWS, Minority")
    is_minority_community: Optional[bool] = Field(False, description="Belongs to recognized minority community")
    is_differently_abled: Optional[bool] = Field(False, description="Person with disability (PwD / UDID holder)")
    is_landowner: Optional[bool] = Field(False, description="Owns cultivable agricultural land")
    land_holding_acres: Optional[float] = Field(None, description="Cultivable landholding in acres")
    has_bank_account: Optional[bool] = Field(True, description="Holds an active bank account")
    is_bank_aadhaar_seeded: Optional[bool] = Field(True, description="Bank account is NPCI Aadhaar seeded for DBT")
    highest_qualification: Optional[str] = Field(None, description="Highest educational qualification attained")
    is_student_currently: Optional[bool] = Field(False, description="Currently enrolled in educational institution or course")
    education_level: Optional[str] = Field(None, description="Education level or stage")
    course: Optional[str] = Field(None, description="Course / degree / trade of study")
    study_year: Optional[int] = Field(None, description="Current year of study (1, 2, 3, etc.)")
    institution_name: Optional[str] = Field(None, description="Name of educational institution or university")


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileResponse(ProfileBase):
    id: str
    completeness_percentage: int = Field(0, description="Calculated profile completeness")

    model_config = ConfigDict(from_attributes=True)
