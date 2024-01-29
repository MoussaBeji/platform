from django.contrib.auth.tokens import PasswordResetTokenGenerator
from datetime import *
import string
import random
import six
from random import randrange
class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user=int(randrange(10000)), timestamp=datetime.now()):
        d=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        return six.text_type(user) + six.text_type(timestamp) + six.text_type(d)


account_activation_token = TokenGenerator()
