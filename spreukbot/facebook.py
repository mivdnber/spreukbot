from urllib.parse import urlencode
import io

import requests
import facebook

import spreukbot.config as config


album_url_template = 'https://graph.facebook.com/v2.11/{}/photos'
fields = [
    'id',
    'images',
    'likes.limit(0).summary(true)',
    # 'comments.limit(10)'
]


def create_album_query(album_id, access_token=config.FACEBOOK_TOKEN):
    return "{}?{}".format(
        album_url_template.format(album_id),
        urlencode(dict(
            fields=fields,
            access_token=access_token
        ))
    )


def fetch(url):
    return requests.get(url).json()


def fetch_album(album_id):
    return fetch(create_album_query(album_id))


def post_update(image):
    page_access_token = config.FACEBOOK_PAGE_TOKEN
    graph = facebook.GraphAPI(page_access_token)
    # facebook_page_id = '562627210891933'
    facebook_page_id = config.FACEBOOK_PAGE_ID
    graph.put_photo(image=io.BytesIO(image), album_path=facebook_page_id + "/photos")
