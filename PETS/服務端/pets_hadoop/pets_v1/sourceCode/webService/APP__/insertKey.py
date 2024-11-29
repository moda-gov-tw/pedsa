#!/usr/bin/python
# -*- coding: utf-8 -*-
import base64
import sys
import re
from config.connect_sql import ConnectSQL


def password_check(password):
    """
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        12 characters length or more
        1 digit or more
        1 uppercase letter or more
        1 lowercase letter or more
    """

    # calculating the length
    length_error = len(password) < 12

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None

    # overall result
    password_ok = not ( length_error or digit_error or uppercase_error or lowercase_error)

    return {
        'password_ok' : password_ok,
        'length_error' : length_error,
        'digit_error' : digit_error,
        'uppercase_error' : uppercase_error,
        'lowercase_error' : lowercase_error
    }



def main():

    # Check password strength
    result = password_check(keyInput)

    if result['password_ok'] is True:
        print('password ok')
    else:
        msg = {
            'length_error': 'Length_error: 12 characters length or more.',
            'digit_error': 'Digit_error: 1 digit or more.',
            'uppercase_error': 'Uppercase_error: 1 uppercase letter or more.',
            'lowercase_error': 'Lowercase_error: 1 lowercase or more.',
        }
        for key in result:
            if result[key] is True:
                print(msg[key])
        print('Password is not available.')
        return False

    # Convert password to base64
    try:
        pwdBase64 = base64.b64encode(keyInput.encode()).decode("utf-8")
    except Exception as e:
        print('Encode base64 error: %s', str(e))
        return False

    # Connect mysql
    try:
        conn = ConnectSQL(userInput, pwdInput)
    except Exception as e:
        print('Connect mysql error: %s', str(e))
        return False

    # Insert to table
    insertValue = {
        'tag': tagInput,
        'key_enc': pwdBase64
    }

    insertResult = conn.insertValue('key_db', 'products', insertValue, False)

    if insertResult['result'] == 1:
        print(insertResult['msg'])
    else:
        print('Insert key fail:' + insertResult['msg'])
        return False

if __name__ == "__main__":
    userInput = sys.argv[1] #str # user id
    pwdInput = sys.argv[2] #str # user password
    tagInput = sys.argv[3] #str # tag for mysql table
    keyInput = sys.argv[4] #str # key for mysql table
    main()

