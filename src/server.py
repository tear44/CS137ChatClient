from network import Listener, Handler, poll
import sys

from threading import Thread
from time import sleep


handlers = {}  # map client handler to user name

class MyHandler(Handler):

    def on_open(self):
        self.do_send('Connection Accepted')
        print('Connected')

    def on_close(self):
        self.do_send('Connection Terminated')


    def on_msg(self, msg):
        # print msg
        # self.do_send('received')
        if (u'txt' in msg):
            if (msg[u'txt'] == ':q'):
                self.do_close()
            else:
                print("%s: %s"%(msg[u'speak'], msg[u'txt']))
                # self.do_send("%s: %s"%(msg[u'speak'], msg[u'txt']))
        elif (u'join' in msg):
            print("%s Joined"%(msg[u'join']))
            # global handlers
            # handlers[self] = msg[u'speak']

class Server(Listener):

    def on_accept(self, h):
        global handlers
        handlers['bob'] = h
        self.handler = h

    def send(self, msg):
        self.handler.do_send(msg)


port = 8888
# server = Listener(port, MyHandler)
server = Server(port, MyHandler)

def periodic_poll():
    while 1:
        poll()
        sleep(0.05)  # seconds

thread = Thread(target=periodic_poll)
thread.daemon = True  # die when the main thread dies
thread.start()

while 1:
    # poll(timeout=0.05) # in seconds
    mytxt = sys.stdin.readline().rstrip()
    server.send({'speak': 'Server', 'txt': mytxt})
    # mytxt = sys.stdin.readline().rstrip()
    # if (mytxt):
    #     server.send(mytxt)

    # sender.do_send({'speak': 'server', 'txt': mytxt})
