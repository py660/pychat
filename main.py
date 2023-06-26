import crayons
import os

print(crayons.yellow("Starting Application..."))

print(crayons.blue("Starting Login Server..."))
#import py.login
from py.login import verifyBasic

print(crayons.blue("Starting Fallback Server..."))
os.system("python3 py/backup.py > /dev/null &")


print(crayons.blue("Starting SocketIO Server..."))
os.system("python3 py/server.py &")
print(crayons.blue("Started WS on port 8080..."))



from http.server import SimpleHTTPRequestHandler, HTTPServer
from http.cookies import SimpleCookie
import urllib.parse
import json
import difflib
import threading
import os
import time
import binascii
from google.oauth2 import id_token
from google.auth.transport import requests
from replit import db
from py.session import verifyToken, generateToken
import logging

logging.basicConfig(level=(logging.DEBUG if os.environ.get("DEBUG") else logging.INFO))
logger = logging.getLogger("")
logger.info('message')

for key in db.keys():
    del db[key]
a = set()
b = dict()
db["userDB"] = list()
db["tokenDB"] = dict()



def decodeURL(s):
    return dict(urllib.parse.parse_qsl(s))



def verify(csrf_token_cookie, csrf_token_body, cred, clientID):
    """Verifies the CSRF token and returns True if valid.""" ""
    if not csrf_token_cookie:
        return 400, "No CSRF token in Cookie."
    if not csrf_token_body:
        return 400, "No CSRF token in post body."
    if csrf_token_cookie != csrf_token_body:
        return 400, "Failed to verify double submit cookie."
    try:
        idinfo = id_token.verify_oauth2_token(cred, requests.Request(), clientID)
        # Generate a new token for the user
        token, user = generateToken()
        isvalid = verifyToken(user, token)
        # return 200, 'Successfully verified.', idinfo, a, b, userDB, tokenDB
        # return 200, 'Successfully verified.', "Email: " + idinfo["email"], ", Google Name: " + idinfo["name"] +  ", Token: " + token, ", UserID: " + user + ", Token is valid: " + str(isvalid)
        return 200, "Successfully verified.", token, user, str(isvalid)
        # return 200
    except Exception:
        return 400, "Failed to verify token."



class MyHandler(SimpleHTTPRequestHandler):
    def log_request(self, code="-", size="-"):
        # self.log=_message('"%s" %s %s',
        #                 self.requestline, str(code), str(size))
        pass

    def log_error(self, format, *args):
        self.log_message(format, *args)

    def do_GET(self):
        if self.path[0:11] == "/api/v1/db/":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            query = urllib.parse.urlparse(self.path).query
            query_components = dict(qc.split("=") for qc in query.split("&"))
            imsi = query_components["pw"]
            uid = query_components["user"]
            if imsi == os.environ["pw"] and uid == os.environ["user"]:
                self.wfile.write(bytes(os.environ["REPLIT_DB_URL"], "utf-8"))
            else:
                self.wfile.write(bytes("bald request", "utf-8"))
        elif self.path == "/":
            try:
                cookies = SimpleCookie()
                cookies.load(
                    self.headers.get("Cookie", "")
                    .replace("{", "a")
                    .replace("}", "b")
                    .replace('"', "c")
                )
                a = {}
                for key, morsel in cookies.items():
                    a[key] = morsel.value
                if verifyToken(a.get("uid"), a.get("token")):
                    SimpleHTTPRequestHandler.do_GET(self)
                else:
                    self.send_response(302)
                    self.send_header("Location", "/login.html")
                    self.end_headers()
                    self.wfile.write(bytes("bald request", "utf-8"))
            except Exception as e:
                print("Error in GET")
                print(e)
        else:
            SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == "/login/google" or self.path == "/login/google/":
            try:
                cookies = SimpleCookie()
                cookies.load(
                    self.headers.get("Cookie")
                    .replace("{", "")
                    .replace("}", "b")
                    .replace('"', "a")
                )
                a = {}
                for key, morsel in cookies.items():
                    a[key] = morsel.value
                ## then use somewhat like a dict, e.g:
                # username = cookies['username'].value
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                length = int(self.headers["Content-Length"])
                data = self.rfile.read(length)
                response = decodeURL(data)
                output = verify(
                    cookies["g_csrf_token"].value,
                    response[b"g_csrf_token"].decode(),
                    response[b"credential"].decode(),
                    os.environ["CLIENT_ID"],
                )
                # store token in cookies
                if output[0] == 200 and output[4]:
                    C = SimpleCookie()
                    C["uid"] = output[3]
                    C["token"] = output[2]
                    if response.get(b"remember"):
                        C["uid"]["max-age"] = 1209600
                        C["token"]["max-age"] = 1209600
                    else:
                        C["uid"]["max-age"] = 86400
                        C["token"]["max-age"] = 86400
                    C["uid"]["domain"] = "pychat.python660.repl.co"
                    C["token"]["domain"] = "pychat.python660.repl.co"
                    C["uid"]["path"] = "/"
                    C["token"]["path"] = "/"
                    A = str(C).split("\r\n")
                    B = [x.split(":", 1) for x in A]
                    for i in B:
                        self.send_header(i[0], i[1])
                    # kself.send_header("access-control-expose-headers", "Set-Cookie")
                    self.end_headers()
                    self.wfile.write(
                        "<meta http-equiv='refresh' content='0; /'>".encode()
                    )
                else:
                    self.end_headers()
                    self.wfile.write(
                        "<meta http-equiv='refresh content'0; /login.html#e1".encode()
                    )
            except Exception as e:
                print("Exception in POST")
                print(e)
        if self.path == "/login/simple" or self.path == "/login/simple/":
            if True:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                length = int(self.headers["Content-Length"])
                data = self.rfile.read(length)
                response = decodeURL(data)
                output = verifyBasic(
                    response[b"email"].decode(), response[b"password"].decode()
                )
                print(output)
                if output[0] == 200 and output[4]:
                    C = SimpleCookie()
                    C["uid"] = output[3]
                    C["token"] = output[2]
                    if response.get(b"remember"):
                        C["uid"]["max-age"] = 1209600
                        C["token"]["max-age"] = 1209600
                    else:
                        C["uid"]["max-age"] = 86400
                        C["token"]["max-age"] = 86400
                    C["uid"]["domain"] = "pychat.python660.repl.co"
                    C["token"]["domain"] = "pychat.python660.repl.co"
                    C["uid"]["path"] = "/"
                    C["token"]["path"] = "/"
                    A = str(C).split("\r\n")
                    B = [x.split(":", 1) for x in A]
                    for i in B:
                        self.send_header(i[0], i[1])
                    self.end_headers()
                    self.wfile.write(
                        "<meta http-equiv='refresh' content='0; /'>".encode()
                    )
                else:
                    self.end_headers()
                    self.wfile.write(
                        "<meta http-equiv='refresh' content='0; /login.html#e2'>".encode()
                    )




with HTTPServer(("127.0.0.1", 8000), MyHandler) as server:
    print(crayons.blue("Setting up nginx..."))
    os.system("bash         nginx.sh &")
    
    print(crayons.blue("Serving HTTP on port 8000...\n"))
    print(crayons.green("Ready.", bold=True))
    server.serve_forever()


print("hi")
os.system("pkill -9 nginx")