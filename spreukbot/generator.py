from collections import defaultdict
import random
import difflib
import io
import textwrap
import urllib.parse

import requests
from PIL import Image, ImageDraw, ImageFont

import spreukbot.rendering as rendering
import spreukbot.facebook as facebook
import spreukbot.config as config


PIXABAY_CATEGORIES = [
    'nature', 'backgrounds', 'people', 'feelings'
]

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


if __name__ == '__main__':
    import sys
    gen = SpreukGenerator('spreukbot/corpus.txt')
    if len(sys.argv) == 2:
        for i in range(int(sys.argv[1])):
            text = gen.generate()
            print(text)
        sys.exit(0)
    print('getting pixabay image')
    image, w, h = random_pixabay()
    print('generating text')
    text = gen.generate()
    print('rendering image')
    png = rendering.render(image, w, h, text)
    print('writing to file')
    with open('spreuk.png', 'wb') as f:
        f.write(png)
    print('showing image')
    facebook.post_update(png)
    Image.open(io.BytesIO(png)).show()
