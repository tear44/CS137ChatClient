#! /usr/bin/env python
from network import Listener, Handler, poll
import sys

from threading import Thread
from time import sleep

#
# Global variables just to make things easier
handlers = {}  # map client handler to user name
users = {}      # map client name to another client name currently in contact
Agent = None    #Assume that the first client connected is the agent, store name
openingLine = {u'speak':'server', u'txt':''''Please enter the number of selected option:\n1) Complaint\t2) Question\t3) Other'''}


# CONTROLLER and Model
class MyHandler(Handler):

    def on_open(self):
        self.do_send('Connection Accepted')
        # self.do_send(openingLine)
        print('Connection Received')

    def on_close(self):
        self.do_send('Connection Terminated')
        global users
        users.pop(self.name)
        print("Bye %s"%(self.name))


    def on_msg(self, msg):
        print msg
        global handlers, users, Agent
        # self.do_send('received')
        # CONTROLLER if joined. adds user name to users and handlers
        if (u'join' in msg):
            self.name = msg[u'join']
            handlers[self.name] = handlers["ADD"]
            print("%s Joined"%(msg[u'join']))
            if (not Agent):
                Agent = self.name
            else:
                users[Agent] = self.name
                users[self.name] = Agent

        #VIEW and CONTROLLER - based on user input, change view accordingly
        elif (u'txt' in msg):
            if (msg[u'txt'] == ':q'):
                self.do_close()
            else:
                ## VIEW - displays to correct terminal
                name = users[self.name]
                if (name in handlers):
                    handlers[name].do_send(msg)
                else:
                    pass

#
class Server(Listener):
    #Signal a new handler with "ADD"
    def on_accept(self, h):
        global handlers
        handlers["ADD"] = h
        self.handler = h

    # def send(self, msg):
    #     self.handler.do_send(msg)
        # handlers['bob'].do_send({u'speak':'T', u'txt':"aaaaaaaaaaaa"})


port = 8888
# server = Listener(port, MyHandler)
server = Server(port, MyHandler)

# def periodic_poll():
#     while 1:
#         poll()
#         sleep(0.05)  # seconds
#
# thread = Thread(target=periodic_poll)
# thread.daemon = True  # die when the main thread dies
# thread.start()

while 1:
    poll(timeout=0.05) # in seconds
    # mytxt = sys.stdin.readline().rstrip()
    # server.send({'speak': 'Server', 'txt': mytxt})
    # mytxt = sys.stdin.readline().rstrip()
    # if (mytxt):
    #     server.send(mytxt)

    # sender.do_send({'speak': 'server', 'txt': mytxt})
