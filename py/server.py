from aiohttp import web
from replit import db
import asyncio
import requests
import socketio, os, binascii, time
#response = requests.get('https://pychat.python660.repl.co/api/v1/db/', params = {'pw': os.environ['pw'], 'user': os.environ['user']}).content.decode()
#if response == "bald request":
#    print("bald request: Incorrect hair data in HEADers")
#    exit()
##print(response)
#db.db_url = response
from google.oauth2 import id_token
from google.auth.transport import requests
#import ssl
db["open"] = "value"

sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins=["https://pychat.python660.repl.co"])
app = web.Application()
sio.attach(app)


#userDB  = set()
#tokenDB = dict()
if not db["userDB"]:
    db["userDB"] = list()
if not db["tokenDB"]:
    db["tokenDB"] = dict()

def verifyToken(user, token):
    """Verifies the token and returns True if valid."""""
    userDB = db["userDB"]
    print(list(userDB))
    tokenDB = db["tokenDB"]
    print(dict(tokenDB))
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
    try:
        userDB = db["userDB"]
        tokenDB = db["tokenDB"]
        user = binascii.b2a_hex(os.urandom(20)).decode()
        if user in userDB:
            del tokenDB[user]
            userDB.remove(user)
        a = binascii.hexlify(os.urandom(20)).decode()
        userDB.append(user)
        tokenDB[user] = {"value": a, "expiry": int(time.time()) + 86400, "iat": int(time.time())} #Used to be 3600 #Now 86400
        db["tokenDB"] = tokenDB
        db["userDB"] = userDB
        return a, user
    except Exception as e:
        print(e)
        return e
        # Error, replace with empty string and check for empty string at the location in which this function was called.


class Processor():
    def __init__(self):
        self.messages = []
        self.currentID = 0

    def process_GET(self):
        content = {"id": [x["id"] for x in self.messages],
                   "messages": self.messages}
        return content

    def process_POST(self, data):
        if data:
            
            if isinstance(data.get("username", False), str) and \
               isinstance(data.get("content", False), str):
                content = "success"
                self.messages.append({"username": data["username"],
                                      "date": str(int(time.time())),
                                      "content": data["content"],
                                      "id": str(self.currentID)})
                print(self.messages)
                self.currentID += 1
            else:
                content = "invalid"
            return content
    



CPU = Processor()


async def background_task():
    """Example of how to send server generated events to clients."""
    await sio.emit('UPDATE', {'time': time.time()})  # Update message list (to none) on server startup.
    count = 0
    while True:
        await sio.sleep(1)
        count += 1
        # await sio.emit('UPDATE', {'time': time.time()})


async def index(request):
    
    #with open('app.html') as f:
        #return web.Response(text=f.read(), content_type='text/html', headers={"Access-Control-Allow-Origin": "https://pychat.python660.repl.co", })
        #token, user = generateToken()
        #isvalid = verifyToken(user, token)
        #return web.Response(text=repr((token, user, isvalid)), content_type='text/html', headers={"Access-Control-Allow-Origin": "https://pychat.python660.repl.co", })
    return web.Response(text="hello people on earth", content_type='text/html', headers={"Access-Control-Allow-Origin": "https://pychat.python660.repl.co", })


async def login(request):
    return web.Response(text="<meta http-equiv='refresh' content='0; javascript: history.back();'>", content_type='text/html', headers={"Access-Control-Allow-Origin": "https://pychat.python660.repl.co", })
        

app.add_routes([web.post('/login', login)])

@sio.on('*')
async def catch_all(event, sid="no-SID", data="none"):
    print(event, sid, data)
    #pass



@sio.event
async def my_event(sid, message):
    await sio.emit('my_response', {'data': message['data']}, room=sid)


@sio.event
async def my_broadcast_event(sid, message):
    await sio.emit('my_response', {'data': message['data']})


def verify(auth):
    #if auth.get("username", False) == "user123" and auth.get("api", False) == "myApiKey":
    #    return True
    return verifyToken(auth.get("uid", False), auth.get("token", False))

@sio.event
async def POST(sid, message):
    print("POST")
    print(sid)
    print(message.get("auth"))
    if not verify(message.get("auth", dict())):
        await sio.emit("401")
        print("None")
        return -1
    await sio.emit('UPDATE', {'time': time.time()})
    await sio.emit('RPLY_POST', CPU.process_POST(message), room=sid)
    

@sio.event
async def GET(sid, message):
    print("GET")
    print(sid)
    print(message)
    if not verify(message.get("auth")):
        await sio.emit("401")
        print("-1")
        return -1
    await sio.emit('RPLY_GET', CPU.process_GET())


#@sio.event
#async def join(sid, message):
#    sio.enter_room(sid, message['room'])
#    await sio.emit('my_response', {'data': 'Entered room: ' + #message['room']},
#                   room=sid)
#
#
#@sio.event
#async def leave(sid, message):
#    sio.leave_room(sid, message['room'])
#    await sio.emit('my_response', {'data': 'Left room: ' + #message['room']},
#                   room=sid)
#
#
#@sio.event
#async def close_room(sid, message):
#    await sio.emit('my_response',
#                   {'data': 'Room ' + message['room'] + ' is #closing.'},
#                   room=message['room'])
#    await sio.close_room(message['room'])
#
#
#@sio.event
#async def my_room_event(sid, message):
#    await sio.emit('my_response', {'data': message['data']},
#                   room=message['room'])


@sio.event
async def disconnect_request(sid):
    await sio.disconnect(sid)


@sio.event
async def connect(sid, environ):
    print("Connected!")
    await sio.emit('my_response', {'data': 'Connected', 'count': 0}, room=sid)


@sio.event
def disconnect(sid):
    print('Client disconnected')


# app.router.add_static('/static', 'static')
#app.router.add_get('/', index)


async def init_app():
    sio.start_background_task(background_task)
    return app


web.run_app(init_app(), host="127.0.0.1", port=8080)