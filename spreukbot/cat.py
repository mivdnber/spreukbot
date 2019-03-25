import random
import base64

import cv2
import requests
import numpy as np
from PIL import Image

import spreukbot.pixabay as pixabay


def detect_cats(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # load the cat detector Haar cascade, then detect cat faces in the input image
    detector = cv2.CascadeClassifier('spreukbot/haarcascade_frontalcatface.xml')
    rects = detector.detectMultiScale(gray, scaleFactor=1.2,
        minNeighbors=12, minSize=(90, 90))

    # loop over the cat faces and draw a rectangle surrounding each
    for (i, (x, y, w, h)) in enumerate(rects):
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(image, "Cat #{}".format(i + 1), (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
    #write the image
    cv2.imwrite('result.jpg', image)
    # show the detected cat faces
    cv2.imshow("Cat Faces", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

image_url, image_width, image_height = pixabay.random_pixabay(
    search='cat face',
    categories=['animals'],
)
image_data = requests.get(image_url, timeout=.3).content
image = np.asarray(bytearray(image_data), dtype="uint8")
image = cv2.imdecode(image, cv2.IMREAD_COLOR)
pillow_image = Image.fromarray(image)
background_image = pixabay.random_pixabay(
    search='background',
    categories=[],
)
print(background_image)
detect_cats(image)


prefixes = [
    # Step one: greeting
    [
        'hallo!',
        'dag baasje!',
        'hey!',
        'miaaaauuuw!',
        'hallo daar!',
        'hier ben ik!',
    ],
    [
        'ik wens je een',
        'ik geef jou een',
        'ik wens jou vandaag een',
        'maak van vandaag een',
        'voor jou een',
        'alleen voor jou',
    ],
]
adjectives = [
    'fijne',
    'leuke',
    'toffe',
    'super',
    'geniale',
    'mega toffe',
    'mega coole',
    'spetterende',
    'geweldige',
]

total = []
for prefix in prefixes:
    if random.random() > .5:
        total.append(random.choice(prefix))

total.append(random.choice(adjectives))
import locale
locale.setlocale(locale.LC_ALL, 'nl_BE')
import calendar
from datetime import datetime
total.append(calendar.day_name[datetime.utcnow().weekday()])
print(f'{" ".join(total).title()}!')

def render(cat_image, background_image, text):
    ugly_text = uglify(text)
    font = random.choice(fonts)
    color = random.choice(colors)
    pixabay_logo = os.path.join(os.getcwd(), 'spreukbot/pixabay-logo.png')
    cat_url, cat_width, cat_height = cat_image
    bg_url, bg_width, bg_height = background_image
    demo_page = f'''
        data:text/html,
        <!doctype html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>LOL</title>
            <link href="https://fonts.googleapis.com/css?family=Pacifico|Baloo+Tamma|Merriweather|Poiret+One" rel="stylesheet">
            <style>
                @page {{
                    margin: 0;
                    size: {cat_width * 3}px {cat_height}px;
                }}
                * {{
                    padding: 0;
                    margin: 0;
                    text-shadow: #FC0 1px 0 10px;
                }}
                html, body {{
                    text-align: center;
                    padding: 0;
                }}
                body:before {{
                    content: "";
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-size: cover;
                    background-image: url('{bg_url.replace('https://pixabay.com', 'http://spreukbot-pixabay.barkr.uk')}');
                    background-repeat: no-repeat;
                }}
                p {{
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    font-family: {font};
                    font-size: 32px;
                    color: {color};
                    text-stroke: 2px white;
                }}
                p.shadow {{
                    color: black !important;
                    top: 1px;
                    left: 1px;
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
                    right: 0;
                    top: 0;
                }}
            </style>
        </head>
        <body>
        <p>text</p>
        <div class="watermark">
            Wijze spreuken om te delen van Marko V. Keten
        </div
        <img class="pixabay" src="cat_url">
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
