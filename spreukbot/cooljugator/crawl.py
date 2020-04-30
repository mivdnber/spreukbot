from dataclasses import dataclass
import requests
from typing import Dict
import sys
import json
import traceback
import time

from bs4 import BeautifulSoup


@dataclass
class Verb:
    pass


def crawl_verb(url: str, session: requests.Session) -> Dict[str, str]:
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    form_elements = soup.select('div.conjugation-cell[data-default][data-form-id][id]')
    raw_forms = {
        form_element['id']: form_element.select('.meta-form')[0].string
        for form_element in form_elements
    }
    return raw_forms


def crawl_index():
    session = requests.Session()
    response = session.get('https://cooljugator.com/nl/list/all')
    soup = BeautifulSoup(response.text, 'html.parser')
    anchors = soup.select('.stacked .item a')
    for anchor in anchors:
        try:
            raw_verb = crawl_verb(f"https://cooljugator.com{anchor['href']}", session)
            print(json.dumps(raw_verb))
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc(file=sys.stderr)
        time.sleep(.3)


if __name__ == '__main__':
    crawl_index()
