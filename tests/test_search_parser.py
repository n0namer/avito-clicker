from avito_clicker.transports.public_search import build_search_url, parse_search_html


def test_build_search_url():
    assert build_search_url("project manager", "moskva") == (
        "https://www.avito.ru/moskva/vakansii?q=project+manager"
    )


def test_parse_marker_cards():
    html = """
    <div data-marker="item" data-item-id="123456789">
      <a data-marker="item-title" href="/moskva/vakansii/project_manager_123456789">
        <span itemprop="name">Project manager</span>
      </a>
      <span data-marker="item-price">от 120 000 ₽</span>
      <span data-marker="item-address">Москва</span>
      <span data-marker="item-company">ООО Тест</span>
    </div>
    """
    rows = parse_search_html(html)
    assert len(rows) == 1
    assert rows[0].source_id == "123456789"
    assert rows[0].title == "Project manager"
    assert rows[0].salary_text == "от 120 000 ₽"
    assert rows[0].location == "Москва"
    assert rows[0].employer == "ООО Тест"
    assert rows[0].url.startswith("https://www.avito.ru/")


def test_parse_json_ld_fallback():
    html = """
    <script type="application/ld+json">
    {
      "@type": "ItemList",
      "itemListElement": [
        {"item": {"@type": "JobPosting", "name": "Ассистент", "url": "/x_987654321", "sku": "987654321"}}
      ]
    }
    </script>
    """
    rows = parse_search_html(html)
    assert [row.source_id for row in rows] == ["987654321"]
    assert rows[0].title == "Ассистент"
