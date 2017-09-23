import sys
from google.cloud import vision
from google.cloud.vision import types


def ocr(path):
    """
    OCRs an image using the Google Cloud Vision API
    """
    client = vision.ImageAnnotatorClient()

    with open(path, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')

    for text in texts:
        print(' "{}"'.format(text.description))

        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices])

        print('bounds: {}'.format(','.join(vertices)))


if __name__ == '__main__':
    ocr(sys.argv[1])
