from fastapi import APIRouter,FastAPI
import secrets
import string


gen = APIRouter()

@gen.get('/genkey')
def genkey():
    sta = 0
    try:
        allow = 'ABCDEF'
        key = ''.join(secrets.choice(allow + string.digits) for x in range(64) )
        return {'status':sta,'msg':'成功','enc_key':key}
    except Exception as e:
        sta = -1
        return {'status':sta,'msg':'系統錯誤' + e,'enc_key':''}
    