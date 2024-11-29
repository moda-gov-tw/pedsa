from fastapi import APIRouter,FastAPI
import secrets
import string

import paramiko
import base64
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_ssh_private_key
from cryptography.hazmat.primitives.serialization import load_ssh_public_key

import logging
logger = logging.getLogger("uvicorn.access")

gen = APIRouter()

@gen.get('/genkey')
def genkey():
    sta = 0
    try:
        allow = 'ABCDEF'
        key = ''.join(secrets.choice(allow + string.digits) for x in range(64) )
        new_key = enc(key)
        logger.info(new_key)
        # dec_key = dec(new_key)
        # logger.info(dec_key)
        return {'status':sta,'msg':'成功','enc_key':new_key}
    except Exception as e:
        sta = -1
        return {'status':sta,'msg':'系統錯誤' + e,'enc_key':''}


def enc(plaintext):

    keyPath="/usr/src/app/ssh_conf/"
    # key_private = paramiko.RSAKey.from_private_key_file(keyPath+"sftp_key.pem",password="iclw200@")
    # private_key = load_ssh_private_key(open(keyPath+"sftp_key.pem", "rb").read(), b"iclw200@")
    public_key = load_ssh_public_key(open(keyPath+"sftp_key.pem.pub", "rb").read(), b"iclw200@")

    ciphertext = public_key.encrypt(
        plaintext.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    encrypted = base64.b64encode(ciphertext)
    return encrypted.decode('utf-8')

    ##############  0718 enc解密  ##############
def dec(base64_encrypted):

    keyPath="/usr/src/app/ssh_conf/"
    # key_private = paramiko.RSAKey.from_private_key_file(keyPath+"sftp_key.pem",password="iclw200@")
    private_key = load_ssh_private_key(open(keyPath+"sftp_key.pem", "rb").read(), b"iclw200@")
    ciphertext = base64.b64decode(base64_encrypted)
    de_ciphertext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return de_ciphertext.decode('utf-8')

    ##############  enc解密  ##############
