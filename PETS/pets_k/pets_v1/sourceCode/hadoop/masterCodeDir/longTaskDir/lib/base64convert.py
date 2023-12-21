import base64
import json


def getJsonParser(jsonBase64__):
    if jsonBase64__ is None:
        return 'input error! getJsonParser input is None!'
    # decode base64
    try:
        de_b64 = base64.b64decode(jsonBase64__)
    except Exception as err:
        return 'decode base64 error! - %s:%s' % (type(err).__name__, err)
    # json parser
    try:
        jsonDic__ = json.loads(de_b64.decode('utf-8'))
        print("Before getJsonParser: ")
        print(jsonBase64__)
        print("After getJsonParser result: ")
        print(jsonDic__)
    except Exception as err:
        return 'json parser error! - %s:%s' % (type(err).__name__, err)
    return jsonDic__


def encodeDic(dictionary__):
    if dictionary__ is None:
        return 'input error! encodeDictionary input is None!'
    try:
        print("Before encodeDic: ")
        print(dictionary__)
        jsonBase64__ = base64.b64encode(json.dumps(dictionary__))
        print("After encodeDic result: ")
        print(jsonBase64__)
    except Exception as err:
        return 'encode error! - %s:%s' % (type(err).__name__, err)

    return jsonBase64__
