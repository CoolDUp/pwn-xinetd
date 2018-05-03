#!/usr/bin/python3 -u
# encoding: utf-8

import random, string, sys, os, time, re, socket
from hashlib import sha256
global tokens
os.chdir(os.path.dirname(os.path.realpath(__file__)))
def check(token):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    if(s.connect((os.getenv('TOKEN_HOST'),int(os.getenv('TOKEN_PORT'))))):
        s.send(token)
        buff = s.recv(4)
        if(buff=="OKAY"):
            return True
    return False           
  
def proof_of_work():
    print("token:")
    x = sys.stdin.read(32)
    if len(x) != 32 or True != check(x):
        return False
    return True
def isUrl(url):
    pattern=re.match(r'(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?',url,re.IGNORECASE)
    if pattern:
        return True
    return False

def token_update(addr):
    global tokens
    if(isUrl(addr)):
        print("not support url yet")
        exit()
    f = open(addr,'r')
    tokens = {}
    for line in f.readlines():
        line = line.strip()
        if not len(line):
            continue
        tokens[line.split(':')[0]] = line.split(':')[1]
    f.close()
   
    print 'Update Tokens ...\n',tokens
    """{name:token,name:token,...}"""

def token_daemon(addr,uptime,port):
    global tokens
    token_update(addr)
    s= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(("0.0.0.0",port))
    s.listen(10)
    t0 = time.time()
    while 1:
        if(time.time() - t0 > uptime):
            token_update(addr)
            t0 = time.time()
        c,a=s.accept()   
        print'Connected by ',a
        while 1:
            data=c.recv(32) 
            if(tokens.has_key(data)):
                c.send("OKAY")
                break
            c.send("FAIL")
            print 'Failed ',data.encode('hex')
            break
        c.close()
            
if __name__ == '__main__':
    if len(sys.argv) != 3:
        if len(sys.argv) == 4:
            token_daemon(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]))
            exit(0)
        print("./token.py prog timeout")
        print("./token.py token_file/token_address update_time Port")
        exit(0)
    if not proof_of_work():
        exit(0)
    else:
        os.execv("/bin/sh", ["sh", "-c", "timeout %s %s 2>/dev/null" % (sys.argv[2], sys.argv[1])])

