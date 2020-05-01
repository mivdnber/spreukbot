from dataclasses import dataclass
import requests
from typing import Dict
import sys
import json
import traceback
import time

from bs4 import BeautifulSoup


start_url = 'https://nl.wiktionary.org/wiki/Categorie:Beroep_in_het_Nederlands'


def crawl_index():
    print('Crawling index', file=sys.stderr)
    session = requests.Session()
    response = session.get(start_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    anchors = soup.select('#toc .external.text')
    for anchor in anchors:
        try:
            crawl_subindex(anchor['href'], session)
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc(file=sys.stderr)
        time.sleep(.3)


def crawl_subindex(url: str, session: requests.Session) -> None:
    print(f'Crawling {url}', file=sys.stderr)
    selector = '.mw-category li a'
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    anchors = soup.select(selector)
    print(anchors, file=sys.stderr)
    for anchor in anchors:
        try:
            crawl_profession(f"https://nl.wiktionary.org{anchor['href']}", session)
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc(file=sys.stderr)


def crawl_profession(url: str, session: requests.Session) -> None:
    print(f'Crawling profession {url}', file=sys.stderr)
    selector_singular = '.infobox tr:nth-child(2) td:nth-child(2)'
    selector_plural = '.infobox tr:nth-child(2) td:nth-child(3)'
    selector_genus = '[title="WikiWoordenboek:Genus"]'
    try:
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        singular = soup.select(selector_singular)[0].getText().strip()
        plural = soup.select(selector_plural)[0].getText().strip()
        try:
            genus = soup.select(selector_genus)[0].getText().strip()
        except IndexError:
            genus = None
        print(json.dumps({"singular": singular, "plural": plural, "genus": genus}))
    except KeyboardInterrupt:
        raise
    except:
        traceback.print_exc(file=sys.stderr)

if __name__ == '__main__':
    crawl_index()
