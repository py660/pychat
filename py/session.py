from replit import db
import binascii
import time
import os

def verifyToken(user, token):
    """Verifies the token and returns True if valid.""" ""
    userDB = list(db["userDB"])
    tokenDB = dict(db["tokenDB"])
    try:
        ## user is uid
        if user in userDB and token:
            if token == tokenDB[user]["value"]:
                if tokenDB[user]["expiry"] > int(time.time()):
                    return True
                else:
                    del tokenDB[user]
                    return False
        return False
    except:
        return False


def generateToken():
    """Generate a token for the user."""
    userDB = list(db["userDB"])
    tokenDB = dict(db["tokenDB"])
    user = binascii.b2a_hex(os.urandom(20)).decode()
    try:
        if user in userDB:
            del tokenDB[user]
            userDB.remove(user)
        a = binascii.hexlify(os.urandom(20)).decode()
        userDB.append(user)
        tokenDB[user] = {
            "value": a,
            "expiry": int(time.time()) + 86400,
            "iat": int(time.time()),
        }  # Used to be 3600 #Now 86400
        db["tokenDB"] = tokenDB
        db["userDB"] = userDB
        return a, user
    except Exception:
        return ""
        # Error, replace with empty string and check for empty string at the location in which this function was called.

