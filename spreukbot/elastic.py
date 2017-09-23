from datetime import datetime
from typing import Union, Mapping, Any, List

from elasticsearch_dsl import connections, DocType, Date, \
    Nested, Boolean, analyzer, InnerDoc, Completion, Keyword, \
    Text, Integer


connections.configure(
    default={'hosts': 'localhost'}
)


def text_with_raw():
    return Text(fields=dict(raw=Keyword()))


class Saying:

    def __init__(
            self,
            saying_id: str,
            url: str,
            attribution: str,
            text: str,
            tags: List[str]=None,
            likes: int=None,
            scraped_at: Union[datetime, None]=None,
            downloaded_at: Union[datetime, None]=None,
            ocrd_at: Union[datetime, None]=None,
            ocr_method: Union[str, None]=None):

        self.saying_id = saying_id
        self.url = url
        self.attribution = attribution
        self.text = text
        self.tags = tags or []
        self.likes = likes
        self.scraped_at = scraped_at or datetime.utcnow()
        self.downloaded_at = downloaded_at
        self.ocrd_at = ocrd_at
        self.ocr_method = ocr_method

    def to_dict(self) -> Mapping[str, Any]:

        def iso_or_none(dt: datetime) -> Union[None, str]:
            return dt and dt.isoformat()

        return {
            **self.__dict__,
            'scraped_at': iso_or_none(self.scraped_at),
            'downloaded_at': iso_or_none(self.downloaded_at),
            'ocrd_at': iso_or_none(self.ocrd_at)
        }


class SayingDoc(DocType):

    class Meta:
        index = 'sayings'

    url = text_with_raw()
    attribution = text_with_raw()
    text = text_with_raw()
    tags = Keyword(multi=True)
    likes = Integer()
    scraped_at = Date()
    downloaded_at = Date()
    ocrd_at = Date()
    ocr_method = Keyword()

    @classmethod
    def generate_index_name(cls) -> str:
        alias_name = cls.get_alias_name()
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f'{alias_name}_{timestamp}'

    @classmethod
    def get_alias_name(cls) -> str:
        return cls._doc_type.index

    def to_plain_object(self) -> Saying:
        return Saying(**self.to_dict())

    @classmethod
    def from_plain_object(cls, obj):
        return cls(**obj.to_dict())


class SayingDatabase:

    doc_type = SayingDoc

    def init(self):
        index_name = self.doc_type.generate_index_name()
        alias_name = self.doc_type.get_alias_name()
        self.doc_type.init(index=index_name)
        es = connections.get_connection()
        es.indices.put_alias(index=index_name, name=alias_name)

    def reindex(self):
        es = connections.get_connection()
        alias = self.doc_type.get_alias_name()
        dest_index = self.doc_type.generate_index_name()
        old_indices = es.indices.get_alias(alias).keys()
        self.doc_type.init(index=dest_index)
        es.reindex(dict(
            source=dict(index=alias),
            dest=dict(index=dest_index)
        ))
        es.indices.update_aliases({
            "actions": [
                {"remove": {"index": old_index, "alias": alias}}
                for old_index in old_indices
            ] + [
                {"add": {"index": dest_index, "alias": alias}}
            ]
        })
