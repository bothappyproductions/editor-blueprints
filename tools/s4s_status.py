"""Read or update a Soles4Souls creator portal's encrypted status (status.enc.json).

usage:
  S4S_PASS=<passcode> python3 s4s_status.py <path/to/status.enc.json>                 # print current overrides
  S4S_PASS=<passcode> python3 s4s_status.py <path/to/status.enc.json> v1Live=true slot="Wed, Nov 11 · 1:00–2:00 PM"
Values: true/false, or text. Keys match the portal's STATUS object (conceptApproved, slot,
fundraisingLink, v1Live, v2Live, storiesLive, paperworkIn, paid, analyticsIn, ...).
The page decrypts this file with the same passcode and applies it on load. Needs: pip install cryptography
"""
import base64, json, os, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

path, sets = sys.argv[1], sys.argv[2:]
passcode = os.environ['S4S_PASS'].strip().lower()
f = json.load(open(path))
salt = base64.b64decode(f['salt'])
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=f['iter']).derive(passcode.encode())
cur = json.loads(AESGCM(key).decrypt(base64.b64decode(f['iv']), base64.b64decode(f['ct']), None))
for s in sets:
    k, v = s.split('=', 1)
    cur[k] = True if v == 'true' else False if v == 'false' else v
if sets:
    iv = os.urandom(12)
    ct = AESGCM(key).encrypt(iv, json.dumps(cur).encode(), None)
    json.dump({'iter': f['iter'], 'salt': f['salt'], 'iv': base64.b64encode(iv).decode(), 'ct': base64.b64encode(ct).decode()}, open(path, 'w'))
print(json.dumps(cur, ensure_ascii=False))
