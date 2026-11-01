import pytest
from backend.app.services.document_service import document_service


def test_document_extraction_and_confirmation():
    """Document parsing requires human confirmation before status becomes verified."""
    upload_resp = document_service.simulate_or_parse_upload(
        "Income_Certificate_Tehsildar.pdf", b"%PDF-1.4 sample content with income certificate"
    )
    assert upload_resp.processing_status == "awaiting_user_confirmation"
    assert upload_resp.is_valid is True
    assert upload_resp.extracted_fields is not None
    assert "annual_family_income" in upload_resp.extracted_fields

    # Confirm extraction
    confirmed = document_service.confirm_extraction(upload_resp.id, {"annual_family_income": "₹ 2,20,000"})
    assert confirmed.processing_status == "verified"
    assert confirmed.user_confirmed_fields["annual_family_income"] == "₹ 2,20,000"


def test_random_document_rejected():
    """Random or non-governmental files are rejected with verification error."""
    resp = document_service.simulate_or_parse_upload(
        "cat_wallpaper.png", b"random binary bytes for an image of a cat"
    )
    assert resp.processing_status == "rejected_unrecognized"
    assert resp.is_valid is False
    assert resp.verification_error is not None
    assert "could not be identified" in resp.verification_error


def test_diverse_document_extraction():
    """Verify Aadhaar, Land Record, and Ration card extract domain-specific fields without percentage placeholder."""
    # Aadhaar
    aadhaar_resp = document_service.simulate_or_parse_upload("My_Aadhaar_Card.pdf", b"%PDF-1.4 mera aadhaar identity")
    assert aadhaar_resp.is_valid is True
    assert aadhaar_resp.detected_type == "Aadhaar Card (UIDAI)"
    assert "document_number" in aadhaar_resp.extracted_fields
    assert "passing_percentage" not in aadhaar_resp.extracted_fields

    # Land Record
    land_resp = document_service.simulate_or_parse_upload("Farmer_Land_7_12_Extract.pdf", b"%PDF-1.4 7/12 khasra land record")
    assert land_resp.is_valid is True
    assert "Land Records" in land_resp.detected_type
    assert "cultivable_land_area" in land_resp.extracted_fields
    assert "passing_percentage" not in land_resp.extracted_fields

    # Ration Card
    ration_resp = document_service.simulate_or_parse_upload("Ration_Card_BPL_NFSA.pdf", b"%PDF-1.4 nfsa bpl ration card")
    assert ration_resp.is_valid is True
    assert "Ration Card" in ration_resp.detected_type
    assert "card_category" in ration_resp.extracted_fields
    assert "passing_percentage" not in ration_resp.extracted_fields


def test_category_mismatch_detection():
    """Uploading a document different from the selected category is strictly rejected."""
    # Aadhaar uploaded when Income Certificate was selected
    aadhaar_mismatch = document_service.simulate_or_parse_upload(
        "Aadhaar_Document.pdf",
        b"%PDF-1.4 UIDAI Mera Aadhaar 9182 3746 5019",
        expected_type="Income Certificate"
    )
    assert aadhaar_mismatch.is_valid is False
    assert aadhaar_mismatch.processing_status == "rejected_category_mismatch"
    assert "Category Mismatch" in aadhaar_mismatch.verification_error
    assert "Income Certificate" in aadhaar_mismatch.verification_error
    assert "Aadhaar Card" in aadhaar_mismatch.detected_type

    # Income Certificate uploaded when Aadhaar Card was selected
    income_mismatch = document_service.simulate_or_parse_upload(
        "Revenue_Income_Cert.pdf",
        b"%PDF-1.4 Tehsildar Income Certificate Rs. 1,50,000",
        expected_type="Aadhaar Card (UIDAI)"
    )
    assert income_mismatch.is_valid is False
    assert income_mismatch.processing_status == "rejected_category_mismatch"
    assert "Category Mismatch" in income_mismatch.verification_error


def test_accurate_fact_extraction_from_pdf():
    """Real facts visibly present on the document are extracted accurately without synthetic placeholders."""
    import pymupdf
    doc = pymupdf.open()
    p = doc.new_page()
    p.insert_text((50, 50), '''GOVERNMENT OF INDIA
Unique Identification Authority of India
Enrollment No: 1024/50214/09872
To,
Vikramjit Singh
S/O Harpreet Singh
DOB: 14/11/1998
Male
9182 3746 5019
Address: H No 214, Model Town, Ludhiana, Punjab - 141002
''')
    pdf_bytes = doc.tobytes()

    res = document_service.simulate_or_parse_upload("Aadhaar_Vikramjit.pdf", pdf_bytes, expected_type="auto")
    assert res.is_valid is True
    assert res.detected_type == "Aadhaar Card (UIDAI)"
    assert res.extracted_fields["document_number"] == "9182 3746 5019"
    assert res.extracted_fields["holder_name"] == "Vikramjit Singh"
    assert res.extracted_fields["date_of_birth"] == "14/11/1998"
    assert res.extracted_fields["gender"] == "Male"
    assert "Ludhiana" in res.extracted_fields["address"]

