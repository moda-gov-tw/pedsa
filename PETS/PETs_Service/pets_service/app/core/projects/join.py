import base64
from fastapi import APIRouter,FastAPI,Body
import secrets
import string
from app.core.projects.base64convert import getJsonParser

join = APIRouter()

#@join.put('/joinfile')
def joinfile(jsonbase64:str = Body(embed=True)):
    sta = 0
    try:
        base = getJsonParser(jsonbase64)
        return base
    except Exception as e:
        sta = -1
        return {'decode error'}