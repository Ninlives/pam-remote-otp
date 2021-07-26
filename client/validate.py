from yubiotp.otp import decode_otp
from binascii import unhexlify

class Validator:
    def __init__(self, public_id, private_id, key, session, counter):
        self.public_id = public_id.encode('utf-8')
        self.private_id = unhexlify(private_id)
        self.key = unhexlify(key)
        self.session = session
        self.counter = counter

    def verify(self, token):
        if isinstance(token, str):
            token = token.encode('utf-8')

        try:
            public_id, otp = decode_otp(token, self.key)
        except Exception:
            return False

        if self.public_id != public_id:
            return False

        if self.private_id != otp.uid:
            return False

        if otp.session < self.session:
            return False

        if otp.session == self.session and otp.counter <= self.counter:
            return False

        self.session = otp.session
        self.counter = otp.counter

        return True
