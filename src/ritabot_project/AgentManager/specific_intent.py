
class Francais():
    """Return the no response intent"""
    def __init__(self):
        pass
    def getdepart(self):
        defaultIntentDepart={
        "name": "Debut de discution",
        "description": "Intent de debut de discution. Message de Bienvenue",


        "question_set": [
            {
                "name": "97b7c09ed472cd10882de674559282dcb7e5c471",

                "order": 1
            }
        ],
        "block_response_set": [
            {
                "is_complex": False,
                "simple_response_set": [
                  {
                    "random_text_set": [
                            {
                                "name": "Pas de reponse specifique. Cette reponse est automatique",
                                "order": 1
                            }
                        ]
                  }
                ]
            }
        ]
        }


        return defaultIntentDepart

    def getdepartfacebook(self):
        defaultIntentDepart={
        "name": "Debut de discution facebook",
        "description": "Intent de debut de discution pour facebook. Message de Bienvenue",


        "question_set": [
            {
                "name": "58108524103242b03af9d44b72dd6b6c9280072e 140ccda42adea5f48c8a617171f3f21d61f6454f",

                "order": 1
            }
        ],
        "block_response_set": [
            {
                "is_complex": False,
                "simple_response_set": [
                  {
                    "random_text_set": [
                            {
                                "name": "Pas de reponse specifique. Cette reponse est automatique pour facebook",
                                "order": 1
                            }
                        ]
                  }
                ]
            }
        ]
        }


        return defaultIntentDepart



    """Return the no response intent"""
    def getnoresponse(self):
        defaultIntentNoResponse={
        "name": "Intent de reponse d'erreur",
        "description": "Intent de reponse d'erreur. Ce message est apparu quand le bot ne trouve pas une reponse pour une tel question",


        "question_set": [
            {
                "name": "e619abf36bd80410b3854c9573fdc63f94a5a942",

                "order": 1
            }
        ],
        "block_response_set": [
            {
                "is_complex": False,
                "simple_response_set": [
                  {
                    "random_text_set": [
                            {
                                "name": "Pas de reponse specifique. Cette reponse est automatique. Vous devez specifier la reponse que vous convienne ici",
                                "order": 1
                            }
                        ]
                  }
                ]
            }
        ]
        }

        return defaultIntentNoResponse


    """Return the disabled intent"""
    def getdisabled(self):
        defaultIntentDisabled={
        "name": "Intent de ponderation",
        "description": "Intent de reponse d'erreur. Ce message est apparu quand le bot ne trouve pas une reponse pour une tel question",


        "question_set": [
            {
                "name": "adc86edc47eba203cc4e1358e7a1f53d2705a263",

                "order": 1
            }
        ],
        "block_response_set": [
            {
                "is_complex": False,
                "simple_response_set": [
                  {
                    "random_text_set": [
                            {
                                "name": "Pas de reponse specifique. Cette reponse est automatique. Vous devez specifier la reponse que vous convienne ici",
                                "order": 1
                            }
                        ]
                  }
                ]
            }
        ]
        }

        return defaultIntentDisabled






"""Langue anglais"""

class Anglais():
    """Return the no response intent"""
    def __init__(self):
        pass
    def getdepart(self):
        defaultIntentDepart={
        "name": "Begin of discussion",
        "description": "Intent of begin of discussion. Welcome message must be specified here",


        "question_set": [
            {
                "name": "97b7c09ed472cd10882de674559282dcb7e5c471",

                "order": 1
            }
        ],
        "block_response_set": [
            {
                "is_complex": False,
                "simple_response_set": [
                  {
                    "random_text_set": [
                            {
                                "name": "No response is specified. This response is generated automatically",
                                "order": 1
                            }
                        ]
                  }
                ]
            }
        ]
        }


        return defaultIntentDepart

    def getdepartfacebook(self):
        defaultIntentDepart={
        "name": "Begin of discussion facebook",
        "description": "Intent of begin of discussion for Facebook. Welcome message must be specified here",


        "question_set": [
            {
                "name": "58108524103242b03af9d44b72dd6b6c9280072e 140ccda42adea5f48c8a617171f3f21d61f6454f",
                "order": 1
            }
        ],
        "block_response_set": [
            {
                "is_complex": False,
                "simple_response_set": [
                  {
                    "random_text_set": [
                            {
                                "name": "No response is specified. This response is generated automatically for facebook",
                                "order": 1
                            }
                        ]
                  }
                ]
            }
        ]
        }


        return defaultIntentDepart



    """Return the no response intent"""
    def getnoresponse(self):
        defaultIntentNoResponse={
        "name": "Error response Intent",
        "description": "Error response Intent. This message appears when the bot does not find an answer for a such question",


        "question_set": [
            {
                "name": "e619abf36bd80410b3854c9573fdc63f94a5a942",

                "order": 1
            }
        ],
        "block_response_set": [
            {
                "is_complex": False,
                "simple_response_set": [
                  {
                    "random_text_set": [
                            {
                                "name": "No response is specified. This response is generated automatically",
                                "order": 1
                            }
                        ]
                  }
                ]
            }
        ]
        }

        return defaultIntentNoResponse


    """Return the disabled intent"""
    def getdisabled(self):
        defaultIntentDisabled={
        "name": "Intent de ponderation",
        "description": "Error response Intent. This message appears when the bot does not find an answer for a such question",

        "question_set": [
            {
                "name": "adc86edc47eba203cc4e1358e7a1f53d2705a263",

                "order": 1
            }
        ],
        "block_response_set": [
            {
                "is_complex": False,
                "simple_response_set": [
                  {
                    "random_text_set": [
                            {
                                "name": "No response is specified. This response is generated automatically",
                                "order": 1
                            }
                        ]
                  }
                ]
            }
        ]
        }

        return defaultIntentDisabled


"""Langue Dialecte tunisien"""

class TunisienDialecte():
    """Return the no response intent"""
    def __init__(self):
        pass
    def getdepart(self):
        defaultIntentDepart={
        "name": "Debut de discution",
        "description": "Intent de debut de discution. Message de Bienvenue",


        "question_set": [
            {
                "name": "97b7c09ed472cd10882de674559282dcb7e5c471",

                "order": 1
            }
        ],
        "block_response_set": [
            {
                "is_complex": False,
                "simple_response_set": [
                  {
                    "random_text_set": [
                            {
                                "name": "Pas de reponse specifique. Cette reponse est automatique",
                                "order": 1
                            }
                        ]
                  }
                ]
            }
        ]
        }


        return defaultIntentDepart

    def getdepartfacebook(self):
        defaultIntentDepart={
        "name": "Debut de discution facebook",
        "description": "Intent de debut de discution pour facebook. Message de Bienvenue",


        "question_set": [
            {
                "name": "58108524103242b03af9d44b72dd6b6c9280072e 140ccda42adea5f48c8a617171f3f21d61f6454f",

                "order": 1
            }
        ],
        "block_response_set": [
            {
                "is_complex": False,
                "simple_response_set": [
                  {
                    "random_text_set": [
                            {
                                "name": "Pas de reponse specifique. Cette reponse est automatique pour facebook",
                                "order": 1
                            }
                        ]
                  }
                ]
            }
        ]
        }


        return defaultIntentDepart



    """Return the no response intent"""
    def getnoresponse(self):
        defaultIntentNoResponse={
        "name": "Intent de reponse d'erreur",
        "description": "Intent de reponse d'erreur. Ce message est apparu quand le bot ne trouve pas une reponse pour une tel question",


        "question_set": [
            {
                "name": "e619abf36bd80410b3854c9573fdc63f94a5a942",

                "order": 1
            }
        ],
        "block_response_set": [
            {
                "is_complex": False,
                "simple_response_set": [
                  {
                    "random_text_set": [
                            {
                                "name": "Pas de reponse specifique. Cette reponse est automatique. Vous devez specifier la reponse que vous convienne ici",
                                "order": 1
                            }
                        ]
                  }
                ]
            }
        ]
        }

        return defaultIntentNoResponse


    """Return the disabled intent"""
    def getdisabled(self):
        defaultIntentDisabled={
        "name": "Intent de ponderation",
        "description": "Intent de reponse d'erreur. Ce message est apparu quand le bot ne trouve pas une reponse pour une tel question",


        "question_set": [
            {
                "name": "adc86edc47eba203cc4e1358e7a1f53d2705a263",

                "order": 1
            }
        ],
        "block_response_set": [
            {
                "is_complex": False,
                "simple_response_set": [
                  {
                    "random_text_set": [
                            {
                                "name": "Pas de reponse specifique. Cette reponse est automatique. Vous devez specifier la reponse que vous convienne ici",
                                "order": 1
                            }
                        ]
                  }
                ]
            }
        ]
        }

        return defaultIntentDisabled


"""Langue arabe"""

class Arabe():
    """Return the no response intent"""
    def __init__(self):
        pass
    def getdepart(self):
        defaultIntentDepart={
        "name": "بداية المحادثة - رسالة الترحيب",
        "description": "بداية المحادثة. رسالة الترحيب الخاصة بالمواقع",


        "question_set": [
            {
                "name": "97b7c09ed472cd10882de674559282dcb7e5c471",

                "order": 1
            }
        ],
        "block_response_set": [
            {
                "is_complex": False,
                "simple_response_set": [
                  {
                    "random_text_set": [
                            {
                                "name": "أدخل رسالة الترحيب هنا",
                                "order": 1
                            }
                        ]
                  }
                ]
            }
        ]
        }


        return defaultIntentDepart

    def getdepartfacebook(self):
        defaultIntentDepart={
        "name": "بداية المحادثة - رسالة الترحيب الخاصة بفيسبوك",
        "description": "بداية المحادثة. رسالة الترحيب الخاصة بفيسبوك",


        "question_set": [
            {
                "name": "58108524103242b03af9d44b72dd6b6c9280072e 140ccda42adea5f48c8a617171f3f21d61f6454f",
                "order": 1
            }
        ],
        "block_response_set": [
            {
                "is_complex": False,
                "simple_response_set": [
                  {
                    "random_text_set": [
                            {
                                "name": "أدخل رسالة الترحيب هنا",
                                "order": 1
                            }
                        ]
                  }
                ]
            }
        ]
        }


        return defaultIntentDepart



    """Return the no response intent"""
    def getnoresponse(self):
        defaultIntentNoResponse={
        "name": "رسالة الأخطاء",
        "description": "تظهر هذه الرسالة إذا أدخل المستعمل سؤال غير مفهوم بالنسبة للتشات بوت ",


        "question_set": [
            {
                "name": "e619abf36bd80410b3854c9573fdc63f94a5a942",

                "order": 1
            }
        ],
        "block_response_set": [
            {
                "is_complex": False,
                "simple_response_set": [
                  {
                    "random_text_set": [
                            {
                                "name": "أدخل رسالة الأخطاء هنا",
                                "order": 1
                            }
                        ]
                  }
                ]
            }
        ]
        }

        return defaultIntentNoResponse


    """Return the disabled intent"""
    def getdisabled(self):
        defaultIntentDisabled={
        "name": "Intent de ponderation",
        "description": "Error response Intent. This message appears when the bot does not find an answer for a such question",

        "question_set": [
            {
                "name": "adc86edc47eba203cc4e1358e7a1f53d2705a263",

                "order": 1
            }
        ],
        "block_response_set": [
            {
                "is_complex": False,
                "simple_response_set": [
                  {
                    "random_text_set": [
                            {
                                "name": "No response is specified. This response is generated automatically",
                                "order": 1
                            }
                        ]
                  }
                ]
            }
        ]
        }

        return defaultIntentDisabled
