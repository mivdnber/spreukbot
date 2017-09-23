import unittest.mock as mock
from datetime import datetime

from spreukbot.elastic import Saying, SayingDoc

present = datetime(2018, 1, 1, 0, 0, 0)
future = datetime(2018, 1, 2, 0, 0, 0)


@mock.patch('spreukbot.elastic.datetime')
def test_to_plain_object_no_scraped_at(dt):
    """
    Test conversion to a plain object when scraped_at is None
    """
    dt.utcnow.return_value = present
    doc = SayingDoc(
        saying_id='abc',
        url='http://google.com',
        attribution='Mooie spreuken om te delen',
        text='LOL SPREUK'
    )
    d = doc.to_plain_object()
    assert d.to_dict() == dict(
        saying_id='abc',
        url='http://google.com',
        attribution='Mooie spreuken om te delen',
        text='LOL SPREUK',
        likes=None,
        tags=[],
        scraped_at='2018-01-01T00:00:00',
        downloaded_at=None,
        ocrd_at=None,
        ocr_method=None
    )


def test_to_plain_object_with_scraped_at():
    doc = SayingDoc(
        saying_id='abc',
        url='http://google.com',
        attribution='Mooie spreuken om te delen',
        text='LOL SPREUK',
        scraped_at=future
    )
    d = doc.to_plain_object()
    assert d.to_dict() == dict(
        saying_id='abc',
        url='http://google.com',
        attribution='Mooie spreuken om te delen',
        text='LOL SPREUK',
        likes=None,
        tags=[],
        scraped_at='2018-01-02T00:00:00',
        downloaded_at=None,
        ocrd_at=None,
        ocr_method=None
    )


def test_from_plain_object():
    obj = Saying(
        saying_id='abc',
        url='http://google.com',
        attribution='Mooie spreuken om te delen',
        text='LOL SPREUK'
    )
    assert isinstance(SayingDoc.from_plain_object(obj), SayingDoc)
