"""utilities for working with timedeltas"""

# pylint: disable=invalid-name
import locale
from datetime import timedelta
from typing import Callable, Dict, Literal, Sequence, Tuple, TypeAlias, TypeVar, Union

T = TypeVar("T", bound="TDC")

TDCKey: TypeAlias = Union[
    Literal["year"],
    Literal["month"],
    Literal["week"],
    Literal["day"],
    Literal["hour"],
    Literal["minute"],
    Literal["second"],
    Literal["microsecond"],
    Literal["millisecond"],
]
LabelDict: TypeAlias = Dict[TDCKey, Tuple[str, str]]


class TDC:
    """TDC: timedelta components"""

    year: int
    month: int
    week: int
    day: int
    hour: int
    minute: int
    second: int
    microsecond: int
    millisecond: int

    keys: Sequence[TDCKey] = (
        "year",
        "month",
        "week",
        "day",
        "hour",
        "minute",
        "second",
        "microsecond",
        "millisecond",
    )

    def __init__(self, td: timedelta):
        for k, v in self.extract_components(td).items():
            setattr(self, k, v)

    def __getitem__(self, key: str) -> int:
        """
        Allow index access to the namedtuple

        Usage:
        >>> t = TDC(timedelta(days=365))
        >>> t['year']
        1
        >>> t['z']
        Traceback (most recent call last):
        ...
        KeyError: 'z'
        """

        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key) from None

    @staticmethod
    def extract_components(td: Union[timedelta, int, float]) -> Dict[str, int]:
        """
        Extracts time components from a timedelta, int, or float.

        Args:
            td: A timedelta object, or an int/float number of seconds.

        Returns:
            A dictionary with keys for years, months, weeks, days, hours,
            minutes, seconds, milliseconds, and microseconds, and values
            representing the number of each in the input timedelta.


        Examples:
            >>> extract_components = TDC.extract_components
            >>> extract_components(timedelta(days=2, seconds=3723))
            {'year': 0, 'month': 0, 'week': 0, 'day': 2, 'hour': 1,
            'minute': 2, 'second': 3, 'millisecond': 0, 'microsecond': 0}
            >>> extract_components(7200)
            {'year': 0, 'month': 0, 'week': 0, 'day': 0, 'hour': 2,
            'minute': 0, 'second': 0, 'millisecond': 0, 'microsecond': 0}
            >>> extract_components(timedelta(days=365))
            {'year': 1, 'month': 0, 'week': 0, 'day': 0, 'hour': 0,
            'minute': 0, 'second': 0, 'millisecond': 0, 'microsecond': 0}
            >>> extract_components(timedelta(days=30))
            {'year': 0, 'month': 1, 'week': 0, 'day': 0, 'hour': 0,
            'minute': 0, 'second': 0, 'millisecond': 0, 'microsecond': 0}
            >>> extract_components(timedelta(hours=48))
            {'year': 0, 'month': 0, 'week': 0, 'day': 2, 'hour': 0,
            'minute': 0, 'second': 0, 'millisecond': 0, 'microsecond': 0}
            >>> extract_components(3600000)
            {'year': 0, 'month': 1, 'week': 1, 'day': 4, 'hour': 16,
            'minute': 0, 'second': 0, 'millisecond': 0, 'microsecond': 0}
            >>> extract_components(timedelta(days=403, seconds=3661, \
            microseconds=1001))
            {'year': 1, 'month': 1, 'week': 1, 'day': 1, 'hour': 1,
            'minute': 1, 'second': 1, 'millisecond': 1, 'microsecond': 1}
        """

        if isinstance(td, (int, float)):
            td = timedelta(seconds=td)

        total_seconds = td.total_seconds()
        sign = -1 if total_seconds < 0 else 1
        total_seconds = abs(total_seconds)

        # define the units and their respective lengths in seconds
        units = (
            ("year", 31_536_000),  # 60 * 60 * 24 * 365
            ("month", 2_592_000),  # 60 * 60 * 24 * 30
            ("week", 604_800),  # 60 * 60 * 24 * 7
            ("day", 86_400),  # 60 * 60 * 24
            ("hour", 3_600),  # 60 * 60
            ("minute", 60),
            ("second", 1),
            ("millisecond", 1e-3),
            ("microsecond", 1e-6),
        )

        components = {}

        for unit, length_in_seconds in units:
            # calculate the number of whole units
            units_total = total_seconds // length_in_seconds

            # add the number of units to the components dict
            components[unit] = sign * int(units_total)

            # subtract the units from the total seconds
            total_seconds -= units_total * length_in_seconds

        return components

    def labeled_values(self, labels: Dict[TDCKey, Tuple[str, str]]) -> Sequence[str]:
        """helper function for languages with a 2-element singular/plural tuple"""
        return [
            f"{self[key]} {labels[key][0] if self[key] == 1 else labels[key][1]}"
            for key in self.keys
            if self[key]
        ]


def duration_to_string_zh(td: timedelta) -> str:
    """
    Convert a timedelta to a Chinese string representation.

    Args:
      td: The timedelta to convert

    Returns:
      A string containing the Chinese representation

    Example:
      >>> from datetime import timedelta
      >>> td = timedelta(days=2, hours=3)
      >>> duration_to_string_zh(td)
      '2天， 3小时'
    """
    tdc = TDC(td)
    labels = {
        "year": "年",
        "month": "个月",
        "week": "周",
        "day": "天",
        "hour": "小时",
        "minute": "分钟",
        "second": "秒",
        "millisecond": "毫秒",
        "microsecond": "微秒",
    }

    # joining with full-width comma then space
    return "\uff0c ".join([f"{tdc[key]}{labels[key]}" for key in tdc.keys if tdc[key]])


def duration_to_string_es(td: timedelta) -> str:
    """
    Convert a timedelta object to a string in Spanish.

    Args:
        td: The timedelta object to convert

    Returns:
        A string with the representation in Spanish

    Example:
        >>> from datetime import timedelta
        >>> td = timedelta(days=2, hours=3)
        >>> duration_to_string_es(td)
        '2 días, 3 horas'
    """
    tdc = TDC(td)
    labels: LabelDict = {
        "year": ("año", "años"),
        "month": ("mes", "meses"),
        "day": ("día", "días"),
        "week": ("semana", "semanas"),
        "hour": ("hora", "horas"),
        "minute": ("minuto", "minutos"),
        "second": ("segundo", "segundos"),
        "millisecond": ("milisegundo", "milisegundos"),
        "microsecond": ("microsegundo", "microsegundos"),
    }
    return ", ".join(tdc.labeled_values(labels))


def duration_to_string_en(td: timedelta) -> str:
    """
    Convert a timedelta to an English string representation.

    Args:
        td: The timedelta object to convert

    Returns:
        A string containing the English representation

    Example:
        >>> from datetime import timedelta
        >>> td = timedelta(days=2, hours=3)
        >>> duration_to_string_en(td)
        '2 days, 3 hours'
    """
    tdc = TDC(td)
    labels: LabelDict = {
        "year": ("year", "years"),
        "month": ("month", "months"),
        "week": ("week", "weeks"),
        "day": ("day", "days"),
        "hour": ("hour", "hours"),
        "minute": ("minute", "minutes"),
        "second": ("second", "seconds"),
        "millisecond": ("millisecond", "milliseconds"),
        "microsecond": ("microsecond", "microseconds"),
    }
    return ", ".join(tdc.labeled_values(labels))


def duration_to_string_hi(td: timedelta) -> str:
    """
    Convert a timedelta to a string representation in Hindi.

    Args:
        td: The timedelta object to convert

    Returns:
        A string containing the representation in Hindi

    Example:
        >>> from datetime import timedelta
        >>> td = timedelta(days=2, hours=3)
        >>> duration_to_string_hi(td)
        '2 दिन, 3 घंटे'
    """
    tdc = TDC(td)
    labels: LabelDict = {
        "year": ("वर्ष", "वर्ष"),
        "month": ("महीना", "महीने"),
        "day": ("दिन", "दिन"),
        "week": ("सप्ताह", "सप्ताह"),
        "hour": ("घंटा", "घंटे"),
        "minute": ("मिनट", "मिनट"),
        "second": ("सेकंड", "सेकंड"),
        "millisecond": ("मिलीसेकंड", "मिलीसेकंड"),
        "microsecond": ("माइक्रोसेकंड", "माइक्रोसेकंड"),
    }
    return ", ".join(tdc.labeled_values(labels))


def duration_to_string_bn(td: timedelta) -> str:
    """
    Convert a timedelta to a string representation in Bengali.

    Args:
        td: The timedelta object to convert

    Returns:
        A string containing the representation in Bengali

    Example:
        >>> from datetime import timedelta
        >>> td = timedelta(days=2, hours=3)
        >>> duration_to_string_bn(td)
        '2 দিন, 3 ঘণ্টা'
    """
    tdc = TDC(td)
    labels: LabelDict = {
        "year": ("বছর", "বছর"),
        "month": ("মাস", "মাস"),
        "week": ("সপ্তাহ", "সপ্তাহ"),
        "day": ("দিন", "দিন"),
        "hour": ("ঘণ্টা", "ঘণ্টা"),
        "minute": ("মিনিট", "মিনিট"),
        "second": ("সেকেন্ড", "সেকেন্ড"),
        "millisecond": ("মিলিসেকেন্ড", "মিলিসেকেন্ড"),
        "microsecond": ("মাইক্রোসেকেন্ড", "মাইক্রোসেকেন্ড"),
    }
    return ", ".join(tdc.labeled_values(labels))


def duration_to_string_pt(td: timedelta) -> str:
    """
    Convert a timedelta object to a string in Portuguese.

    Args:
        td: The timedelta object to convert

    Returns:
        A string containing the representation in Portuguese

    Example:
        >>> from datetime import timedelta
        >>> td = timedelta(days=2, hours=3)
        >>> duration_to_string_pt(td)
        '2 dias, 3 horas'
    """
    tdc = TDC(td)
    labels: LabelDict = {
        "year": ("ano", "anos"),
        "month": ("mês", "meses"),
        "week": ("semana", "semanas"),
        "day": ("dia", "dias"),
        "hour": ("hora", "horas"),
        "minute": ("minuto", "minutos"),
        "second": ("segundo", "segundos"),
        "millisecond": ("milissegundo", "milissegundos"),
        "microsecond": ("microssegundo", "microssegundos"),
    }
    return ", ".join(tdc.labeled_values(labels))


def duration_to_string_ja(td: timedelta) -> str:
    """Convert a timedelta object to a string in Japanese.

    Args:
        td: The timedelta object to convert

    Returns:
        A string containing the representation in Japanese

    Example:
        >>> from datetime import timedelta
        >>> td = timedelta(days=2, hours=3)
        >>> duration_to_string_ja(td)
        '2日、3時間'
    """
    tdc = TDC(td)
    labels: Dict[TDCKey, str] = {
        "year": "年",
        "month": "ヶ月",
        "week": "週間",
        "day": "日",
        "hour": "時間",
        "minute": "分",
        "second": "秒",
        "millisecond": "ミリ秒",
        "microsecond": "マイクロ秒",
    }
    return "、".join([f"{tdc[key]}{labels[key]}" for key in tdc.keys if tdc[key]])


def duration_to_string_mr(td: timedelta) -> str:
    """
    Convert a timedelta object to a string in Marathi.

    Args:
        td: The timedelta object to convert

    Returns:
        A string containing the representation in Marathi

    Example:
        >>> from datetime import timedelta
        >>> td = timedelta(days=2, hours=3)
        >>> duration_to_string_mr(td)
        '2 दिवस, 3 तास'
    """
    tdc = TDC(td)
    labels: Dict[TDCKey, str] = {
        "year": "वर्ष",
        "month": "महिने",
        "week": "आठवडे",
        "day": "दिवस",
        "hour": "तास",
        "minute": "मिनिटे",
        "second": "सेकंद",
        "microsecond": "मायक्रोसेकंद",
        "millisecond": "मिलीसेकंद",
    }
    return ", ".join([f"{tdc[key]} {labels[key]}" for key in tdc.keys if tdc[key]])


def duration_to_string_ru(td: timedelta) -> str:
    """
    Convert a timedelta object to a string in Russian.

    Args:
        td: The timedelta object to convert

    Returns:
        A string containing the representation in Russian

    Example:
        >>> from datetime import timedelta
        >>> td = timedelta(days=2, hours=3)
        >>> duration_to_string_ru(td)
        '2 дня, 3 часа'
    """
    tdc = TDC(td)
    labels: Dict[TDCKey, Tuple[str, str, str]] = {
        "year": ("год", "года", "лет"),
        "month": ("месяц", "месяца", "месяцев"),
        "week": ("неделя", "недели", "недель"),
        "day": ("день", "дня", "дней"),
        "hour": ("час", "часа", "часов"),
        "minute": ("минута", "минуты", "минут"),
        "second": ("секунда", "секунды", "секунд"),
        "millisecond": ("миллисекунда", "миллисекунды", "миллисекунд"),
        "microsecond": ("микросекунда", "микросекунды", "микросекунд"),
    }

    def pluralize_ru(quantity: int, singular: str, few: str, many: str) -> str:
        """handler for the three forms of pluralization in RU"""
        if quantity % 10 == 1 and quantity % 100 != 11:
            return f"{quantity} {singular}"
        if quantity % 10 in [2, 3, 4] and quantity % 100 not in [12, 13, 14]:
            return f"{quantity} {few}"
        return f"{quantity} {many}"

    return ", ".join(
        [pluralize_ru(tdc[key], *labels[key]) for key in tdc.keys if tdc[key]]
    )


def duration_to_string_vi(td: timedelta) -> str:
    """
    Convert a timedelta object to a string in Vietnamese.

    Args:
        td: The timedelta object to convert

    Returns:
       A string containing the representation in Vietnamese

    Example:
        >>> from datetime import timedelta
        >>> td = timedelta(days=2, hours=3)
        >>> duration_to_string_vi(td)
        '2 ngày, 3 giờ'
    """

    tdc = TDC(td)
    labels: Dict[TDCKey, str] = {
        "year": "năm",
        "month": "tháng",
        "week": "tuần",
        "day": "ngày",
        "hour": "giờ",
        "minute": "phút",
        "second": "giây",
        "millisecond": "mili giây",
        "microsecond": "micro giây",
    }
    return ", ".join([f"{tdc[key]} {labels[key]}" for key in tdc.keys if tdc[key]])


def duration_to_string_tr(td: timedelta) -> str:
    """
    Convert a timedelta object to a string in Turkish.

    Args:
        td: The timedelta object to convert

    Returns:
        A string containing the representation in Turkish

    Example:
        >>> from datetime import timedelta
        >>> td = timedelta(days=2, hours=3)
        >>> duration_to_string_tr(td)
        '2 gün, 3 saat'
    """
    tdc = TDC(td)
    labels: LabelDict = {
        "year": ("yıl", "yıl"),
        "month": ("ay", "ay"),
        "week": ("hafta", "hafta"),
        "day": ("gün", "gün"),
        "hour": ("saat", "saat"),
        "minute": ("dakika", "dakika"),
        "second": ("saniye", "saniye"),
        "millisecond": ("milisaniye", "milisaniyeler"),
        "microsecond": ("mikrosaniye", "mikrosaniyeler"),
    }
    return ", ".join(tdc.labeled_values(labels))


def locale_dict() -> Dict[str, str]:
    """Return a dictionary with locale information.

    Returns:
        dict: Locale info with keys:
            - locale_name: Full locale name string
            - encoding: Locale encoding
            - lang_code: ISO 639 language code
            - territory_code: ISO 3166 territory code

    Example:
        >>> locale_dict()['lang_code']
        'en'
    """
    locale_name, encoding = locale.getlocale()

    if locale_name:
        lang_code, territory_code = locale_name.split("_", 1)
    else:
        lang_code = ""
        territory_code = ""

    return {
        "locale_name": locale_name if locale_name else "",
        "encoding": encoding if encoding else "",
        "lang_code": lang_code,
        "territory_code": territory_code,
    }


def duration_to_string(td: timedelta, localize: bool = True) -> str:
    """
    return the given timedelta in a verbose, human-readable string format
    """

    # working my way down this list:
    # https://en.wikipedia.org/wiki/List_of_languages_by_number_of_native_speakers
    handlers: Dict[str, Callable[[timedelta], str]] = {
        "zh": duration_to_string_zh,  # Chinese (zh) - 1.3 billion speakers
        "es": duration_to_string_es,  # Spanish (es) - 442 million speakers
        "en": duration_to_string_en,  # English (en) - 372 million speakers
        "hi": duration_to_string_hi,  # Hindi (hi) - 341 million speakers
        "pt": duration_to_string_pt,  # Portuguese (pt) - 234 million speakers
        "bn": duration_to_string_bn,  # Bengali (bn) - 228 million speakers
        "ru": duration_to_string_ru,  # Russian (ru) - 153 million speakers
        "ja": duration_to_string_ja,  # Japanese (ja) - 128 million speakers
        "vi": duration_to_string_vi,  # Vietnamese (vi) - 85 million speakers
        "tr": duration_to_string_tr,  # Turkish (tr) - 84 million speakers
        "mr": duration_to_string_mr,  # Marathi (mr) - 83 million speakers
    }
    handler = handlers.get(locale_dict().get("lang_code", "en") if localize else "en")
    if handler is None:
        raise RuntimeError("encountered an issue with the locale")
    return handler(td)
