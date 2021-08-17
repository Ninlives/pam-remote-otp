import json
import hashlib
import uuid
import http.client
from validate import Validator

def doAuth(pamh, argv):
    try:
        secret_file = argv[1]
        state_dir   = argv[2]
        base_url    = argv[3]

        with open(secret_file) as f:
            secret  = json.load(f)
        try:
            with open(f'{state_dir}/counters.json') as f:
                counter = json.load(f)
        except FileNotFoundError:
            counter = {}
        
        public_id  = secret['public-id']
        private_id = secret['private-id']
        key        = secret['key']

        digest = hashlib.sha256(bytes(f'{public_id}_{private_id}_{key}', 'utf-8')).hexdigest()

        if digest not in counter:
            counter[digest] = { 'session': 0, 'counter': 0 }

        validator = Validator(public_id, private_id, key, counter[digest]['session'], counter[digest]['counter'])
        sid = str(uuid.uuid4())
        
        site = http.client.HTTPSConnection(base_url)
        site.request('GET', f'/new_session/{sid}')
        if not json.load(site.getresponse())['Success']:
            pamh.conversation(pamh.Message(pamh.PAM_ERROR_MSG, 'Failed to create new session.'))
            return pamh.PAM_AUTH_ERR

        pamh.conversation(pamh.Message(pamh.PAM_TEXT_INFO, f'Session: {sid}'))
        while True:
            site.request('GET', f'/get_otp/{sid}')
            response = json.load(site.getresponse())

            if not response['Success'] and response['Code'] == 1:
                return pamh.PAM_AUTH_ERR

            if response['Success']:
                if validator.verify(response['OTP']):
                    counter[digest]['session'] = validator.session
                    counter[digest]['counter'] = validator.counter
                    with open(f'{state_dir}/counters.json', 'w') as f:
                        json.dump(counter, f)
                    return pamh.PAM_SUCCESS
                else:
                    return pamh.PAM_AUTH_ERR
    except Exception as e:
        pamh.conversation(pamh.Message(pamh.PAM_ERROR_MSG, f'Error: {e}'))

def pam_sm_authenticate(pamh, flags, argv):
	"""Called by PAM when the user wants to authenticate, in sudo for example"""
	return doAuth(pamh, argv)


def pam_sm_open_session(pamh, flags, argv):
	"""Called when starting a session, such as su"""
	return doAuth(pamh, argv)


def pam_sm_close_session(pamh, flags, argv):
	"""We don't need to clean anyting up at the end of a session, so returns true"""
	return pamh.PAM_SUCCESS


def pam_sm_setcred(pamh, flags, argv):
	"""We don't need set any credentials, so returns true"""
	return pamh.PAM_SUCCESS
