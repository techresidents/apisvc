from rest.format.base import Format
from rest.format.json import JsonFormatter

class FormatterFactory(object):
    def create(self, format, buffer, api=None):
        if format == Format.JSON:
            return JsonFormatter(buffer, api)
