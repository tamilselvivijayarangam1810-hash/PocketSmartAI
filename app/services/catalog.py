from urllib.parse import quote_plus


def search_url(platform: str, query: str) -> str:
    q = quote_plus(query)
    urls = {
        "Amazon": f"https://www.amazon.in/s?k={q}",
        "Flipkart": f"https://www.flipkart.com/search?q={q}",
        "IKEA": f"https://www.ikea.com/in/en/search/?q={q}",
        "Swiggy": f"https://www.swiggy.com/search?query={q}",
        "Zomato": f"https://www.zomato.com/search?q={q}",
        "OYO": f"https://www.oyorooms.com/search?location={q}",
    }
    return urls.get(platform, f"https://www.google.com/search?q={quote_plus(platform + ' ' + query)}")


HOME_CATALOG = [
    ("IKEA", "study table", 4500), ("Amazon", "LED ceiling light", 1200),
    ("Amazon", "ceiling fan", 2600), ("IKEA", "dining chair", 3200),
    ("IKEA", "side table", 2800), ("Amazon", "wall decor", 900),
    ("Amazon", "curtain set", 1400), ("IKEA", "storage cabinet", 6500),
]

PARTY_CATALOG = [
    ("Swiggy", "party catering meal", 250), ("Zomato", "party catering meal", 300),
    ("Amazon", "party decoration kit", 1200), ("Amazon", "balloon decoration", 800),
    ("OYO", "event accommodation", 2200),
]

JEWELRY_CATALOG = [
    ("Amazon", "minimal gold-tone earrings", 799),
    ("Flipkart", "pearl necklace set", 1299),
    ("Amazon", "statement earrings", 999),
    ("Flipkart", "traditional necklace set", 1899),
    ("Amazon", "bracelet", 699),
]
