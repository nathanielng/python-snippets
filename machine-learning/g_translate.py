#!/usr/bin/env python

# Dependencies:
# pip -qq install googletrans

import googletrans

from googletrans import Translator


class GTranslate():

    def __init__(self):
        self._translator = Translator()

    def supported_languages(self):
        supported_languages = googletrans.LANGUAGES
        return list(supported_languages.keys())

    def translate(self, txt: str, dest: str = 'en'):
        result = self._translator.translate(txt, dest=dest)
        return [result.origin, result.src, result.text]


if __name__ == "__main__":
    GT = GTranslate()
    print('Supported languages:')
    print(','.join(GT.supported_languages()))
    print('Example translation:')
    print(GT.translate('水'))
