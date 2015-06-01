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
CLIENTS = []    #A python list to hold the clients, current and in line

def next_Client():
    '''Global function to move and set next client in line'''
    global CLIENTS, Agent, users, handlers
    current = CLIENTS.pop(0)
    users[Agent] = current['name']
    users[current['name']] = Agent
    info = 'Now connecting to client %s for %s, on topic "%s"' %(current['name'],
                                                            current['msg'][u'Need'],
                                                            current['msg'][u'text'])
    handlers[Agent].do_send({u'info' : info})


# CONTROLLER and Model
class MyHandler(Handler):

    def on_open(self):
        self.do_send('Connecting you with an agent to assist you')
        print('Connection Received')

    def on_close(self):
        self.do_send('Client has left the chat')
        global users, CLIENTS
        # users.pop(str(self.name))
        # print("Bye %s"%(self.name))

        if (len(CLIENTS)):
            next_Client()


    def on_msg(self, msg):
        print msg
        global handlers, users, Agent, CLIENTS

        # CONTROLLER if joined. adds user name to users and handlers
        if (u'join' in msg):
            self.name = msg[u'join']
            handlers[self.name] = handlers["ADD"]

            if (not Agent):
                Agent = self.name
                users[Agent] = None
                handlers[self.name].do_send({u'status' : 'Agent'})
                print("Agent %s has joined"%(msg[u'join']))
            else:
                handlers[self.name].do_send({u'status' : 'Client'})
                print("%s Joined"%(msg[u'join']))
                if (users[Agent] == None):
                    users[Agent] = self.name
                    users[self.name] = Agent
                else: #New user is gonna have to wait....
                    pass

        elif (u'Need' in msg):
            if (users[Agent] != self.name):
                CLIENTS.append({'name': self.name, 'msg': msg})
            else:
                info = 'Now connecting to client %s for %s, on topic "%s"' %(self.name,
                                                                        msg[u'Need'],
                                                                        msg[u'text'])
                handlers[Agent].do_send({u'info' : info})

            self.do_send({u'info':'You would like option: ' + msg[u'Need'] + '. \nChecking for available agent now..'})

        #VIEW and CONTROLLER - based on user input, change view accordingly
        elif (u'txt' in msg):
            ## VIEW - displays to correct terminal
            if (self.name in users):
                name = users[self.name]
                if (name in handlers):
                    if (self.name == Agent):
                        msg[u'speak'] = 'Agent'
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
