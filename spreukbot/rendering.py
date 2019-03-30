import time
import signal
import random
import logging
import os

import spreukbot


package_directory = os.path.dirname(os.path.abspath(__file__))
colors = ["pink", "yellow", "red", "green", "orange"]
fonts = [
    "'Baloo Tamma', cursive",
    "'Merriweather', serif",
    "'Poiret One', cursive",
    "Pacifico"
]


def uglify(text):
    longest_words = sorted(set(text.split()), key=lambda x: -len(x))
    ugly_pattern = '<span style="color: {}; font-family: {}">{}</span>'
    for word in longest_words[:2]:
        color = random.choice(colors)
        font = random.choice(fonts)
        text = text.replace(word, ugly_pattern.format(color, font, word))
    return text


class WeasyprintLoggerFilter(logging.Filter):

    def filter(self, record):
        print(record.getMessage())
        return True


def render(image_url, image_width, image_height, text, emoji=""):
    ugly_text = uglify(text)
    font = random.choice(fonts)
    color = random.choice(colors)
    pixabay_logo = os.path.join(os.getcwd(), 'spreukbot/pixabay-logo.png')
    emoji_font_path = os.path.join(package_directory, 'fonts/noto/NotoColorEmoji.ttf')
    demo_page = f'''
        data:text/html,
        <!doctype html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>LOL</title>
            <link href="https://fonts.googleapis.com/css?family=Pacifico|Baloo+Tamma|Merriweather|Poiret+One|Noto+Sans" rel="stylesheet">
            <style>
                @font-face {{
                    font-family: 'Noto Emoji';
                    font-style: normal;
                    font-weight: 300;
                    src: url('file://{emoji_font_path}') format('ttf');
                }}
                @page {{
                    margin: 0;
                    size: {image_width}px {image_height}px;
                }}
                * {{
                    padding: 0;
                    margin: 0;
                    text-shadow: #FC0 1px 0 10px;
                }}
                html, body {{
                    text-align: center;
                    padding: 0;
                    height: 100%;
                }}
                body:before {{
                    content: "";
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-size: cover;
                    background-image: url({image_url.replace('https://pixabay.com', 'http://spreukbot-pixabay.barkr.uk')});
                    background-repeat: no-repeat;
                }}
                p.saying {{
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    font-family: {font};
                    font-size: 32px;
                    color: {color};
                }}
                p.saying.shadow {{
                    color: black !important;
                    top: 1px;
                    left: 1px;
                }}
                p.emoji {{
                    position: absolute;
                    bottom: 10%;
                    left: 0;
                    width: 100%;
                    text-align: center;
                    font-family: 'Noto Emoji', sans-serif;
                    font-size: 54px;
                }}
                div.watermark {{
                    position: absolute;
                    right: 10%;
                    bottom: 10%;
                    transform: rotate(-45deg);
                    opacity: .2;
                    width: 20%;
                }}
                img.pixabay {{
                    position: absolute;
                    left: 0;
                    bottom: 0;
                }}
            </style>
        </head>
        <body>
        <p class="emoji">{emoji}</p>
        <p class="saying shadow">{ugly_text}</p>
        <p class="saying">{ugly_text}</p>
        <div class="watermark">
            Wijze spreuken om te delen van Marko V. Keten
        </div
        <img class="pixabay" src="file://{pixabay_logo}">
        </body>
        </html>
    '''
    from weasyprint import HTML
    from weasyprint.logger import LOGGER as weasyprint_logger
    import logging
    logging.getLogger('weasyprint').setLevel(logging.DEBUG)
    weasyprint_logger.addFilter(WeasyprintLoggerFilter())
    weasyprint_logger.setLevel(logging.DEBUG)
    data = HTML(string=demo_page).write_png()
    return data
