import random

import requests

import spreukbot.config as config


PIXABAY_CATEGORIES = ["nature", "backgrounds", "people", "feelings"]


def random_pixabay(categories=None, search=None):
    params = {
        "key": config.PIXABAY_KEY,
        "safesearch": "true",
        "order": "latest",
        "per_page": 200,
        "category": random.choice(categories or PIXABAY_CATEGORIES),
    }

    if search is not None:
        params["q"] = search

    response = requests.get(config.PIXABAY_URL, params, timeout=2.0)
    results = response.json()
    hit = random.choice(results["hits"])
    url = hit["webformatURL"]
    # image_data = requests.get(url, timeout=2.0).content
    return hit["webformatURL"], hit["webformatWidth"], hit["webformatHeight"]
