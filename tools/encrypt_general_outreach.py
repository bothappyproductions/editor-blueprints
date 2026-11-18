"""Re-encrypt the Storytelling Call Desk data (run locally, never commit the plain JSON).
usage: python encrypt_general_outreach.py accounts.json people.json "<passcode>"
writes call-desk/general-outreach/data.enc.json  (needs: pip install cryptography)"""
import sys,json,gzip,os,base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
acc,ppl,pw=sys.argv[1:4]
raw=gzip.compress(json.dumps({'accounts':json.load(open(acc)),'people':json.load(open(ppl))},separators=(',',':')).encode())
salt,iv,it=os.urandom(16),os.urandom(12),250000
key=PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=salt,iterations=it).derive(pw.encode())
env={'v':1,'iter':it,'salt':base64.b64encode(salt).decode(),'iv':base64.b64encode(iv).decode(),'ct':base64.b64encode(AESGCM(key).encrypt(iv,raw,None)).decode()}
out=os.path.join(os.path.dirname(__file__),'..','call-desk','general-outreach','data.enc.json')
json.dump(env,open(out,'w')); print('wrote',out)
