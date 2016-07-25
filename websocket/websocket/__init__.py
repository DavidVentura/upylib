# https://tools.ietf.org/html/rfc6455

# length is a shortcut for not doing chunk encoding
# TODO: understand chunk encoding
header = """HTTP/1.x 200 OK
Connection: Keep-Alive
Content-Type: text/html; charset=UTF-8
Content-Length: {length}

"""

page = b'''
<html>
    <head>
        <title>Micropython WebSocket Test</title>
        <script language="Javascript">

            function on_load() {
                // alert("what the fuck!");
                document.getElementById("console").innerHTML += "started<BR/>";

                var conn = new WebSocket("ws://localhost");
                document.getElementById("console").innerHTML += "created socket<BR/>";

                conn.onopen = function () {
                    conn.send("ping");
                }

                conn.onerror = function (error) {
                    console.log("Websocket error: " + error);
                }

                conn.onmessage = function (msg) {
                    document.getElementById("console").innerHTML += msg+"<BR/>";
                }

            }


        </script>
    </head>
    <body onload="on_load()">
        <DIV id="console">tester<BR/></DIV>
    </body>
</html>
'''

# passed an http request (header[,body])
# returns request, {options_dict}, body
def parse_http_request(msg):
    from io import BytesIO
    f = BytesIO(msg)
    request = str(f.readline().strip(), "utf-8")
    # request_type = str(request.split(b' ')[0].upper(), 'utf-8')
    options = {}
    while True:
        option = f.readline()
        if option in (b"", b"\r\n"):
            break
        else:
            opt,val = option.split(b":",1)
            opt = str(opt.strip(), "utf-8")
            val = str(val.strip(), "utf-8")
            options[ opt ] = bytes(val, "utf-8") #leave clean values as bytes 
    body = ""
    while True:
        line = f.readline()
        if line == b"": # EOF
            break
        else:
            body += line
    f.close()
    return request, options, body
    

from .sha1 import sha1
magic = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

addr = ('0.0.0.0', 80)
s.bind( socket.getaddrinfo(addr[0],addr[1])[0][-1] )
s.listen(3)

conn, addr = s.accept()

req = conn.recv(4096)
print(req)

conn.send(bytes(header.format(length=str(len(page))),"utf-8"))
conn.send(page)

# get the new websocket request from the page
conn, addr = s.accept()

req = conn.recv(4096)
# print(':', req)

r,o,b = parse_http_request(req)
print(r)
for i in o:
    print(i, o[i])
print(b)

from binascii import *

response = b"HTTP/1.x 101 Switching Protocols\r\n"

c=b"dGhlIHNhbXBsZSBub25jZQ==258EAFA5-E914-47DA-95CA-C5AB0DC85B11"  

# generate options
options = {}
# server should reject sessions who's Origin doesn't want to process
# Options["Origin"] # RFC doesn't specifically say this required, but probably is
# options["Host"] = o["Host"] # RFC doesn't specifically say this required, but probably is
options["Upgrade"] = b"websocket"
options["Connection"] = b"Upgrade"
# unclear why this process appends an unexpected \n
options["Sec-WebSocket-Accept"] = \
    b2a_base64(unhexlify(sha1(o["Sec-WebSocket-Key"] + magic)))[:-1]
if "Sec-Websocket-Extensions" in o:
    # client should fail connection on mismatch
    options["Sec-WebSocket-Extensions"] = o["Sec-WebSocket-Extensions"]
if "Sec-WebSocket-Protocol" in o:
    # client should fail connection on mismatch
    options["Sec-WebSocket-Protocol"] = o["Sec-WebSocket-Protocol"]

opts = b""
for key in options:
    opts += bytes(key,"utf-8") + b": " + options[key] + b"\r\n"

print(opts)

conn.send(response + opts + b"\r\n")

resp = conn.recv(1024) # should receive 'ping'

def bytes_to_int(b): #big-endian
    i = 0
    for b8 in b:
        i <<= 8
        i += b8
    return i

# bitfields, not using ucstruct for c compat
# and due to subsequent variable length fields
def parse_websocket_frame(frame):
    mf = memoryview(frame)
    ptr = 0
    fin = bool( mf[ptr] & (1<<7) )
    # ignore bitfields reserved for future
    opcode = mf[ptr] & 0b1111
    ptr += 1
    use_mask = bool( mf[ptr] & (1<<7) )
    length = mf[ptr] & 0x7f
    if length == 126:
        length = bytes_to_int( mf[ptr+1:ptr+1+2] )
        ptr += 1+2
    elif length == 127:
        length = bytes_to_int( mf[ptr+1:ptr+1+4] )
        ptr += 1+4
    else:
        ptr += 1
    mask = mf[ptr:ptr+4]
    ptr += 4
    if use_mask:
        # client to server msg
        msg = "" # what about non text messages?
        for i in range(len(mf[ptr:])):
            msg += chr( mf[ptr+i]^mask[i%4] )
    else:
        # server to client msg
        msg = mf[ptr:]
    return fin, opcode, msg 
    
print( parse_websocket_frame(resp) )
