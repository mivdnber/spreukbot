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
import spreukbot.pixabay as pixabay


logger = logging.getLogger('spreukbot')


def ngram(n, text):
    words = text.split()
    return zip(*[words[x:] for x in range(n)])


EMOJI = [
    '😂',
    '😍',
    '😜',
    '😩',
    '😠',
    '💩',
    '💘',
    '💔',
]


def get_random_emoji():
    count = random.choice([0, 0, 0, 0, 1, 2, 3])
    return random.choice(EMOJI) * count


class SpreukGenerator:
    def __init__(self, source):
        with open(source) as f:
            self.lines = [l for l in f]
        self.mc = defaultdict(list)
        for line in self.lines:
            for a, b, c in ngram(3, line):
                self.mc[(a,b)].append(c)
                self.mc[(a.lower(),b.lower())].append(c)
        print(self.mc)
    @property
    def starting_words(self):
        return [k for k in self.mc.keys() if k[0].istitle()]

    def random_start(self):
        print(len(set(self.starting_words)), 'possible starting words')
        return random.choice(self.starting_words)

    def generate(self, max_iterations=30, max_retries=5, min_length=9, accept_length=14):
        output = ''
        while len(output.split()) < min_length:
            state = self.random_start()
            output = ' '.join(state)
            while self.mc[state] and max_iterations:
                word = random.choice(self.mc[state])
                output += ' ' + word
                print(output)
                state = (state[1], word)
                if word.endswith(('.', '!')) and len(output.split()) > accept_length:
                    print("ending")
                    break
                max_iterations -= 1
        if not max_iterations or not self.unique(output):
            print(f'Rejected; trying {max_retries} more time(s)')
            return self.generate(max_retries=max_retries - 1)
        return output.strip()

    def unique(self, spreuk):
        return all(
            difflib.SequenceMatcher(a=spreuk, b=line).ratio() < .55 \
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
    image, w, h = pixabay.random_pixabay()
    logger.info('generating text')
    text = gen.generate()
    logger.info('rendering image')
    emoji = get_random_emoji()
    png = rendering.render(image, w, h, text, emoji=emoji)
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