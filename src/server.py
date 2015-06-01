#! /usr/bin/env python

# MODEL SCRIPT - Server Script acts as our Model

from network import Listener, Handler, poll
import sys

from threading import Thread
from time import sleep


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
    handlers[current['name']].do_send({u'info': 'Now Connected to an Agent'})


class MyHandler(Handler):

    def on_open(self):
        self.do_send('Connecting you with an agent to assist you')
        print('Connection Received')

    def on_close(self):
        self.do_send('Client has left the chat')
        global users, CLIENTS
        users[Agent] = None

        if (self.name in users):
            users.pop(self.name)
        # print("Bye %s"%(self.name))

        if (len(CLIENTS)):
            next_Client()


    def on_msg(self, msg):
        print msg
        global handlers, users, Agent, CLIENTS

        #Client Joins
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

        #Client Specifies what he needs
        elif (u'Need' in msg):
            self.do_send({u'info':'You would like option: ' + msg[u'Need']})

            if (users[Agent] != self.name):
                CLIENTS.append({'name': self.name, 'msg': msg})
                self.do_send({u'info':'Agent is currently busy, please wait...'})
            else:
                info = 'Now connecting to client %s for %s, on topic "%s"' %(self.name,
                                                                        msg[u'Need'],
                                                                        msg[u'text'])
                handlers[Agent].do_send({u'info' : info})
                handlers[self.name].do_send({u'info': 'Now connected to an agent'})

        #Client Sends in some text
        elif (u'txt' in msg):
            if (self.name in users):
                name = users[self.name]
                if (name in handlers):
                    if (self.name == Agent):
                        msg[u'speak'] = 'Agent'
                    handlers[name].do_send(msg)
                else:
                    pass

        #:e option
        elif (u'extra' in msg):
            self.do_send({u'info': 'trolololololol'})
            print("Troll Feature!")

        #:q quit
        elif (u'exit' in msg):
            if (self.name == Agent):
                Agent = None

        #:s save log file
        elif (u'save' in msg):
            self.do_send({u'info': 'Check for log file in current directory, or where client script is located'})




class Server(Listener):
    #Signal a new handler with "ADD"
    def on_accept(self, h):
        global handlers
        handlers["ADD"] = h
        self.handler = h


port = 8888
server = Server(port, MyHandler)


while 1:
    poll(timeout=0.05) # in seconds
