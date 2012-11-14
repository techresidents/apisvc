from rest.format.base import Format
from rest.format.json import JsonFormatter

class FormatterFactory(object):
    def create(self, format, buffer):
        if format == Format.JSON:
            return JsonFormatter(buffer)
