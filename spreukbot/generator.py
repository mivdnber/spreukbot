from collections import defaultdict
import random
import difflib
import io
import textwrap
import urllib.parse
import logging

import requests
from PIL import Image, ImageDraw, ImageFont
import click

import spreukbot.rendering as rendering
import spreukbot.facebook as facebook
import spreukbot.config as config

PIXABAY_CATEGORIES = [
    'nature', 'backgrounds', 'people', 'feelings'
]

logger = logging.getLogger('spreukbot')


def ngram(n, text):
    words = text.split()
    return zip(*[words[x:] for x in range(n)])


def random_pixabay():
    params = {
        'key': config.PIXABAY_KEY,
        'safesearch': 'true',
        'order': 'latest',
        'per_page': 200,
        'category': random.choice(PIXABAY_CATEGORIES)
    }
    results = requests.get(config.PIXABAY_URL, params, timeout=2.0).json()
    hit = random.choice(results['hits'])
    url = hit['webformatURL']
    image_data = requests.get(url, timeout=2.0).content
    return hit['webformatURL'], hit['webformatWidth'], hit['webformatHeight']


class SpreukGenerator:
    def __init__(self, source):
        with open(source) as f:
            self.lines = [l for l in f]
        self.mc = defaultdict(list)
        for line in self.lines:
            for a, b, c in ngram(3, line):
                self.mc[(a,b)].append(c)

    def random_start(self):
        return random.choice([k for k in self.mc.keys() if k[0].istitle()])

    def generate(self, max_iterations=30, max_retries=5, min_length=9):
        output = ''
        while len(output.split()) < min_length:
            state = self.random_start()
            output = ' '.join(state)
            while self.mc[state] and max_iterations:
                word = random.choice(self.mc[state])
                output += ' ' + word
                state = (state[1], word)
                max_iterations -= 1
        if not max_iterations or not self.unique(output):
            return self.generate(max_retries=max_retries - 1)
        return output.strip()

    def unique(self, spreuk):
        return all(
            difflib.SequenceMatcher(a=spreuk, b=line).ratio() < .45 \
                and spreuk not in line
            for line in self.lines
        )



@click.command()
@click.option('--post/--no-post', default=False)
@click.option('--file', default=None)
@click.option('--show/--no-show', default=False)
@click.option('--count', default=None, type=int)
def main(post, file, show, count):    
    gen = SpreukGenerator('spreukbot/corpus.txt')
    if count is not None:
        for i in range(count):
            text = gen.generate()
            print(text)
        sys.exit(0)
    logger.info('getting pixabay image')
    image, w, h = random_pixabay()
    logger.info('generating text')
    text = gen.generate()
    logger.info('rendering image')
    png = rendering.render(image, w, h, text)
    if file is not None:
        logger.info('writing to file')
        with open(file, 'wb') as f:
            f.write(png)
    if show:
        logger.info('showing image')
        Image.open(io.BytesIO(png)).show()
    if post:
        facebook.post_update(png)

if __name__ == '__main__':
    main()