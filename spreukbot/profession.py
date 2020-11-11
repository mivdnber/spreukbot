from __future__ import annotations

from importlib import resources
import json
import random
from typing import Sequence, Dict, NamedTuple, Callable, List, Union, Any
import typing
import logging
from typing_extensions import Annotated
from enum import Enum
import inspect
import io
from PIL import Image
import click

import spreukbot.pixabay as pixabay
import spreukbot.rendering as rendering
import spreukbot.facebook as facebook


class Gift(NamedTuple):
    base: str
    demonstrative: str
    english: str

    @property
    def as_demonstrative(self) -> str:
        return f"{self.demonstrative} {self.base}"

    def __format__(self, modifiers) -> str:
        if "demonstrative" in modifiers:
            return self.as_demonstrative
        else:
            return self.base


class Gender(Enum):
    MALE = "m"
    FEMALE = "v"
    NEUTRAL = "o"
    NONE = None


class Profession(NamedTuple):
    singular: str
    plural: str
    gender: Gender

    def __format__(self, modifiers):
        if "plural" in modifiers:
            return self.plural
        else:
            return self.singular

    @property
    def as_dict(self) -> Dict[str, Any]:
        return {
            **self._asdict(),
            "gender": self.gender.value,
        }


class Verb:
    def __init__(self, raw_verb_dict: Dict[str, str]):
        self._raw_verb_dict = raw_verb_dict

    @property
    def infinitive(self) -> str:
        return (
            self._raw_verb_dict.get("present4_bijzin")
            or self._raw_verb_dict["present4"]
        )

    def __format__(self, modifiers) -> str:
        if "infinitive" in modifiers:
            return self.infinitive
        if "_bijzin" in modifiers:
            try:
                return self._raw_verb_dict[modifiers]
            except KeyError:
                return self._raw_verb_dict[modifiers.replace("_bijzin", "")]
        else:
            return self._raw_verb_dict[modifiers]


class AdjectiveGender(NamedTuple):
    singular: str
    plural: str


class Adjective:
    def __init__(self, base: str, adjective_genders: Dict[Gender, AdjectiveGender]):
        self._base = base
        self._adjective_genders = adjective_genders

    # def __format__(self, modifiers) -> str:
    #     if "female" in modifiers:
    #         gender = Gender.FEMALE
    #     elif "neutral" in modifiers:
    #         gender = Gender.NEUTRAL
    #     elif "male" in modifiers:
    #         gender = Gender.MALE
    #     else:
    #         gender = None

    #     if "plural" in modifiers:
    #         pass


def _load_jsonl(filename: str) -> Sequence[Dict[str, str]]:
    with resources.open_text("spreukbot.data", filename) as f:
        lines = f.readlines()
    return [json.loads(l) for l in lines]


def load_professions() -> Sequence[Profession]:
    raw_professions = _load_jsonl("professions.jsonl")
    return [
        Profession(
            singular=raw_profession["singular"],
            plural=raw_profession["plural"],
            gender=Gender(raw_profession["gender"]),
        )
        for raw_profession in raw_professions
    ]


def load_verbs() -> Sequence[Verb]:
    raw_verbs = _load_jsonl("verbs.jsonl")
    return [Verb(raw_verb) for raw_verb in raw_verbs]


def load_gifts() -> Sequence[Gift]:
    return [
        Gift(base="roos", demonstrative="deze", english="rose"),
        Gift(base="bloem", demonstrative="deze", english="flower"),
        Gift(base="chocolaatjes", demonstrative="deze", english="chocolates"),
        Gift(base="duif", demonstrative="deze", english="dove"),
        Gift(base="kaars", demonstrative="deze", english="candle"),
    ]


def load_adjectives() -> Sequence[str]:
    with resources.open_text("spreukbot.data", "adjectives.txt") as f:
        return f.read().split()


KindType = Union[Verb, Profession, Gift, Adjective]


class RenderedTemplate(NamedTuple):
    arguments: Dict[str, Union[KindType, List[KindType]]]
    text: str


class Templates:
    def __init__(self):
        self._templates = []
        self._collections = {
            Verb: load_verbs(),
            Profession: load_professions(),
            Gift: load_gifts(),
            Adjective: load_adjectives(),
        }

    def __call__(self, template_function: Callable[..., str]):
        self._templates.append(template_function)

    def random(self) -> RenderedTemplate:
        template = random.choice(self._templates)
        return self._render(template)

    def _render(self, template: Callable[..., str]) -> RenderedTemplate:
        type_hints = typing.get_type_hints(template)
        arguments: Dict[str, Union[KindType, List[KindType]]] = {}
        for name, type_hint in type_hints.items():
            if name != "return":
                arguments[name] = self._select(type_hint)
        return RenderedTemplate(arguments=arguments, text=template(**arguments),)

    def _select(self, type_hint) -> Union[KindType, List[KindType]]:
        if type_hint in self._collections:
            return random.choice(self._collections[type_hint])
        else:
            length = type_hint.__metadata__[0].n
            kind = type_hint.__origin__.__args__[0]
            return random.choices(self._collections[kind], k=length)


template = Templates()


class Len(NamedTuple):
    n: int


@template
def _(
    verb: Verb,
    gift: Gift,
    profession: Profession,
    adjective: Adjective,
    verbs: Annotated[List[Verb], Len(2)],
) -> str:
    return (
        f"Ik geef {gift:demonstrative} aan alle {profession:plural} "
        f"die in deze moeilijke tijden {adjective} voor ons "
        f"blijven {verb:infinitive}."
    )


@template
def _(
    verb: Verb,
    gift: Gift,
    profession: Profession,
    adjective: Adjective,
    verbs: Annotated[List[Verb], Len(2)],
) -> str:
    upper_gift = f"{gift:demonstrative}".upper()
    percentage = random.randint(90, 99)
    return (
        f"Van iedere mens die dit ziet zal {percentage}% {gift:demonstrative} niet delen. "
        f"Als jij een hart hebt voor de {profession} die {adjective} "
        f"voor ons {verb:present3_bijzin}, DEEL DAN {upper_gift}!"
    )


def fix_problem(profession: Profession) -> Profession:
    prefix = profession.singular
    print("fixing", profession)
    for i in range(len(profession.singular)):
        prefix = profession.singular[: -1 - i]
        if profession.plural.count(prefix) > profession.singular.count(prefix):
            break
    else:
        print(profession)
    fixed_plural = prefix + profession.plural.split(prefix)[1]
    return Profession(
        singular=profession.singular, plural=fixed_plural, gender=profession.gender,
    )


@click.command()
@click.option("--post/--no-post", default=False)
@click.option("--file", default=None)
@click.option("--show/--no-show", default=False)
def main(post, file, show):
    logger = logging.getLogger("spreukbot")
    logger.info("generating text")
    template_wrapper = template.random()
    gift = template_wrapper.arguments["gift"]
    logger.info(f"getting image (searching for {gift.english}")
    image_url, width, height = pixabay.random_pixabay(search=gift.english)
    logging.info("rendering png")
    png = rendering.render(image_url, width, height, template_wrapper.text)
    if file is not None:
        logger.info("writing to file")
        with open(file, "wb") as f:
            f.write(png)
    if show:
        logger.info("showing image")
        Image.open(io.BytesIO(png)).show()
    if post:
        logger.info("posting to facebook")
        facebook.post_update(png)


if __name__ == "__main__":
    main()
