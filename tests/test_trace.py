from avito_clicker.trace import parse_post_data, redact_value, sanitize_url


def test_redact_sensitive_json_values():
    payload = {
        "vacancy_id": 123,
        "resume_id": 456,
        "phone": "+79990000000",
        "profile": {"email": "x@example.com", "experience": 3},
    }
    redacted = redact_value(payload)
    assert redacted["vacancy_id"] == 123
    assert redacted["resume_id"] == 456
    assert redacted["phone"] == "<redacted>"
    assert redacted["profile"]["email"] == "<redacted>"
    assert redacted["profile"]["experience"] == 3


def test_sanitize_url_query():
    url = sanitize_url("https://www.avito.ru/api/x?vacancyId=123&token=abc&otp=999")
    assert "vacancyId=123" in url
    assert "abc" not in url
    assert "999" not in url


def test_parse_post_json_preserves_structure():
    parsed = parse_post_data('{"vacancy_id":123,"message":"hello"}')
    assert parsed == {"vacancy_id": 123, "message": "<redacted>"}
