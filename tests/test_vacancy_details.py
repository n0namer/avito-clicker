from avito_clicker.transports.vacancy_details import parse_vacancy_html


def test_parse_jobposting_json_ld():
    html = """
    <script type="application/ld+json">
    {
      "@type": "JobPosting",
      "title": "Операционный директор",
      "url": "/moskva/vakansii/x_123456789",
      "identifier": "123456789",
      "description": "Управлять операционной деятельностью",
      "datePosted": "2026-08-12",
      "hiringOrganization": {"name": "Тест"},
      "jobLocation": {"address": {"addressLocality": "Москва"}},
      "baseSalary": {"currency": "RUB", "value": {"minValue": 150000, "maxValue": 220000, "unitText": "MONTH"}}
    }
    </script>
    """
    vacancy = parse_vacancy_html(html, "https://www.avito.ru/moskva/vakansii/x_123456789")
    assert vacancy is not None
    assert vacancy.source_id == "123456789"
    assert vacancy.title == "Операционный директор"
    assert vacancy.employer == "Тест"
    assert vacancy.location == "Москва"
    assert "150000" in (vacancy.salary_text or "")
