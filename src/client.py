#! /usr/bin/env python

from network import Handler, poll
import sys
from threading import Thread
from time import sleep

typeofchat = {'1':'Comment', '2':'Question', '3':'Complaint', '4':'Other'}
myname = raw_input('What is your name? \n')
ip = raw_input('What is the ip address of the server? (or localhost) \n')

#Boolean flags for control
choice = None
chattopic = None
topic_chosen_orAgent = False


## VIEW - Everything in this class
class Client(Handler):

    def on_open(self):
        self.log = []

    def on_close(self):
        print('Now exiting!')
        sys.exit()

    def on_msg(self, msg):
        if (u'info' in msg):
            print(msg[u'info'])
            self.log.append(msg[u'info'])
        elif (u'txt' in msg):
            print("%s: %s"%(msg[u'speak'], msg[u'txt']))
            self.log.append("%s: %s"%(msg[u'speak'], msg[u'txt']))
        elif (u'status' in msg):
            self.log.append("Welcome %s" %(msg[u'status']))
            if (msg[u'status'] == 'Agent'):
                print("Welcome Agent")
                global topic_chosen_orAgent
                topic_chosen_orAgent = True
            else:
                print("Welcome Client")
        elif (u'close' in msg):
            print('Server Down, shutting service off')
            self.log.append('Server Down, shutting service off')
            sys.exit()


def writetoFile(client):
    '''Writes the collected log lines to a file '''
    with open('chatlog.txt', 'w') as f:
        for line in client.log:
            f.write(line + '\n')


### CONTROLLER - Everything below

#Port and socket control settings
# host, port = 'localhost', 8888
host, port = ip, 8888
client = Client(host, port)
client.do_send({'join': myname})

def periodic_poll():
    while 1:
        poll()
        sleep(0.05)  # seconds

thread = Thread(target=periodic_poll)
thread.daemon = True  # die when the main thread dies
thread.start()

#Input control settings
while 1:
    mytxt = sys.stdin.readline().rstrip()
    if (topic_chosen_orAgent):
        #Extra option
        if mytxt == ':e':
            client.do_send({u'extra': 'Troll Activated'})

        #Save log file option
        elif mytxt == ':s':
            client.do_send({u'save': 'save log'})
            writetoFile(client)

        #Quit Option
        elif mytxt.lower() == ':q':
            print('Now exiting!')
            client.do_send({u'speak': myname, u'txt': "User has left"})
            client.do_send({u'exit': myname})
            sys.exit()

        #Regular text to agent or server
        else:
            client.do_send({u'speak': myname, u'txt': mytxt})
            client.log.append("%s: %s"%(myname, mytxt))

    #Initial Set of questions to be sent to server
    else:
        choice = raw_input('How may I help you today? \n1)Comment \n2)Question \n3)Complaint \n4)Other\n')
        if (choice not in typeofchat):
            while (choice not in typeofchat):
                choice = raw_input('Please input a valid option. \n1)Comment \n2)Question \n3)Complaint \n4)Other\n')
        chattopic = raw_input('What is the topic you would like to discuss today?\n')
        client.do_send({u'Need': typeofchat[choice], u'text': chattopic})
        topic_chosen_orAgent = True
