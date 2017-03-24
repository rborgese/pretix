import json
from contextlib import contextmanager

from django.conf import settings
from django.utils import translation
from django.utils.formats import date_format, number_format
from django.utils.translation import ugettext
from i18nfield.fields import (  # noqa
    I18nCharField, I18nTextarea, I18nTextField, I18nTextInput,
)
from i18nfield.forms import I18nFormField  # noqa
# Compatibility imports
from i18nfield.strings import LazyI18nString  # noqa
from i18nfield.utils import I18nJSONEncoder  # noqa


class LazyDate:
    def __init__(self, value):
        self.value = value

    def __format__(self, format_spec):
        return self.__str__()

    def __str__(self):
        return date_format(self.value, "SHORT_DATE_FORMAT")


class LazyNumber:
    def __init__(self, value, decimal_pos=2):
        self.value = value
        self.decimal_pos = decimal_pos

    def __format__(self, format_spec):
        return self.__str__()

    def __str__(self):
        return number_format(self.value, decimal_pos=self.decimal_pos)


@contextmanager
def language(lng):
    _lng = translation.get_language()
    translation.activate(lng or settings.LANGUAGE_CODE)
    try:
        yield
    finally:
        translation.activate(_lng)


class LazyLocaleException(Exception):
    def __init__(self, msg, msgargs=None):
        self.msg = msg

        if isinstance(msgargs, list) or isinstance(msgargs, tuple) or isinstance(msgargs, dict):
            msgargs = json.dumps(msgargs, cls=I18nJSONEncoder)

        self.msgargs = msgargs
        super().__init__(msg, self.msgargs)

    def __str__(self):
        if self.msgargs:
            data = json.loads(self.msgargs)
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, dict):
                        data[k] = LazyI18nString(v)
            elif isinstance(data, list):
                for i, v in enumerate(data):
                    if isinstance(v, dict):
                        data[i] = LazyI18nString(v)

            return ugettext(self.msg) % data
        else:
            return ugettext(self.msg)
