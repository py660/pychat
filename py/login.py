if True:
    import firebase_admin
    from firebase_admin import credentials, firestore
    import os
    import bcrypt
    import crayons
    import json
    from py.session import generateToken, verifyToken
    data = os.environ['json_data']
    projectId = os.environ['projectId']
    jsonData = json.loads(data)
    cred = credentials.Certificate(jsonData)
    firebase_admin.initialize_app(cred, {'projectId': projectId})
    db = firestore.client()
    userdb = db.collection('users')
    print(crayons.green("Database Loaded..."))

# Define a function for firebase authentication
def login(email, userpw):
    try:
        # Authenticate the user
        user = str(email).replace(" ", "").lower()
        doc = userdb.document(user).get()
        check_alg = os.environ['pw_check_alg']
        data = doc.to_dict()
        print("\nLogging in as " + data["fname"] + " ...")
        if doc.exists and eval(check_alg).decode() == data["password"]:
            return data["verified"]
        return False
    except Exception as e:
        print(e)
        return False

def verifyBasic(email, pw):
    """Verifies the basic auth credentials and returns True if valid."""
    try:
        valid = login(email, pw)
        if not valid:
            return 401, "Invalid credentials."
        token, user = generateToken()
        isvalid = verifyToken(user, token)
        return 200, "Succesfully verified.", token, user, str(isvalid)
    except Exception:
        return 401, "Invalid credentials."

if __name__ == "__main__":
    #print(auth("omg@gmail.com", "123456"))
    pass


try:
    os.remove("/tmp/serviceAccount.json")
    print(crayons.red("Recovered from crash or SGKILL. Please don't do this in the future.", bold=True))
except Exception:
    pass