from googletrans import Translator, LANGUAGES
# from google.cloud import translate_v2 as translate
# import six
# from google.api_core.exceptions import PermissionDenied, ClientError, ServerError, Forbidden

# pip install google-cloud-translate
# pip install googletrans
# {
#     "ar": "arabic",
#     "fr": "french",
#     "en": "english"
#
# }

class GoogleTranslate():
    # library documentation : # https://py-googletrans.readthedocs.io/en/latest/
    def __init__(self):
        # self.translator = Translator(['translate.google.com', 'translate.google.co.kr'], timeout=2)
        pass

    def translate(self, text, source_language, target_language):

        try:
            translator = Translator(['translate.google.com', 'translate.google.co.kr'], timeout=2)
        except:
            return text
        try:
            result = translator.translate(text, src=source_language, dest=target_language)
            result = result.text
        except:
            result = text
        return result

# g = GoogleTranslate().translate("salut", "fr", "en")
# print(g)


##### START : Google cloud Translate V2 basic
# import os
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'/home/solixy/anaconda3/envs/ritabot_23_01_2020/bin/groovy-reserve-275208-13e55d180457.json'
#
# class GoogleCloudTranslateV2:
#     # official documentation : https://cloud.google.com/translate/docs/basic/translating-text
#     def __init__(self):
#         self.translate_client = translate.Client()
#
#     def list_languages(self):
#         # en-US, fr
#         """Lists all available languages."""
#         results = self.translate_client.get_languages()
#
#         for language in results:
#             print(u'{name} ({language})'.format(**language))
#         return results
#
#     def detect_language(self, text):
#         """Detects the text's language."""
#         # Text can also be a sequence of strings, in which case this method
#         # will return a sequence of results for each text.
#         result = self.translate_client.detect_language(text)
#
#         print('Text: {}'.format(text))
#         print('Confidence: {}'.format(result['confidence']))
#         print('Language: {}'.format(result['language']))
#         return result["language"]
#
#     def translate_text(self, text, target_language_code):
#         """Translates text into the target language.
#         Target must be an ISO 639-1 language code.
#         See https://g.co/cloud/translate/v2/translate-reference#supported_languages
#         """
#
#         if isinstance(text, six.binary_type):
#             text = text.decode('utf-8')
#
#         # Text can also be a sequence of strings, in which case this method
#         # will return a sequence of results for each text.
#         try:
#             result = self.translate_client.translate(
#                 text, target_language=target_language_code)
#
#             print(u'Text: {}'.format(result['input']))
#             print(u'Translation: {}'.format(result['translatedText']))
#             print(u'Detected source language: {}'.format(
#                 result['detectedSourceLanguage']))
#
#             return result["translatedText"]
#
#         except ServerError:
#             print("500")
#             return ""
#         except ClientError:
#             print("400")
#             return ""


##### END : Google cloud Translate V2



##### START Google cloud translate advanced

# class GoogleCloudTranslate:
#     # official documentation : https://cloud.google.com/translate/docs/advanced/translating-text-v3
#     def __init__(self):
#         self.client = translate.TranslationServiceClient()
#         self.project_id = '[Google Cloud Project ID]'
#
#     def detect_language(self, text):
#         """
#         Detecting the language of a text string
#
#         Args:
#           text The text string for performing language detection
#         """
#         parent = self.client.location_path(self.project_id, "global")
#
#         response = self.client.detect_language(
#             content=text,
#             parent=parent,
#             mime_type='text/plain'  # mime types: text/plain, text/html
#         )
#         # Display list of detected languages sorted by detection confidence.
#         # The most probable language is first.
#         for language in response.languages:
#             # The language detected
#             print(u"Language code: {}".format(language.language_code))
#             # Confidence of detection result for this language
#             print(u"Confidence: {}".format(language.confidence))
#             return language.language_code
#
#     def get_supported_languages(self):
#         """Getting a list of supported language codes"""
#
#         parent = self.client.location_path(self.project_id, "global")
#
#         response = self.client.get_supported_languages(parent=parent)
#
#         # List language codes of supported languages
#         print('Supported Languages:')
#         for language in response.languages:
#             print(u"Language Code: {}".format(language.language_code))
#         return response.languages
#
#     def translate_text(self, text, source_language, target_language):
#         """
#         Translating Text
#
#         Args:
#           text The content to translate in string format
#           target_language Required. The BCP-47 language code to use for translation.
#         """
#
#
#         # TODO(developer): Uncomment and set the following variables
#         contents = [text]
#         parent = self.client.location_path(self.project_id, "global")
#         try:
#             response = self.client.translate_text(
#                 parent=parent,
#                 contents=contents,
#                 mime_type='text/plain',  # mime types: text/plain, text/html
#                 source_language_code=source_language,
#                 target_language_code=target_language)
#             # Display the translation for each input text provided
#             for translation in response.translations:
#                 print(u"Translated text: {}".format(translation.translated_text))
#                 return translation.translated_text
#
#         except ServerError:
#             print("500")
#             return ""
#         except ClientError:
#             print("400")
#             return ""

##### END Google cloud translate