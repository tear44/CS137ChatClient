#! /usr/bin/env python

from network import Handler, poll
import sys
from threading import Thread
from time import sleep

typeofchat = {'1':'Comment', '2':'Question', '3':'Complaint', '4':'Other'}
myname = raw_input('What is your name? ')
# choice = raw_input('How may I help you today? \n1)Comment \n2)Question \n3)Complaint \n4)Other\n')
# if (choice not in typeofchat):
#     while (choice not in typeofchat):
#         choice = raw_input('Please input a valid option. \n1)Comment \n2)Question \n3)Complaint \n4)Other\n')
# chattopic = raw_input('What is the topic you would like to discuss today?\n')

choice = None
chattopic = None

topic_chosen_orAgent = False

## VIEW: class Client handles what the user sees as they chat with an agent
class Client(Handler):

    def on_close(self):
        print('Now exiting!')
        sys.exit()

    def on_msg(self, msg):
        # print msg
        if (u'info' in msg):
            print(msg[u'info'])
        elif (u'txt' in msg):
            print("%s: %s"%(msg[u'speak'], msg[u'txt']))
        elif (u'status' in msg):
            if (msg[u'status'] == 'Agent'):
                print("Welcome Agent")
                global topic_chosen_orAgent
                topic_chosen_orAgent = True
            else:
                print("Welcome Client")
                # global choice, chattopic
                # choice = raw_input('How may I help you today? \n1)Comment \n2)Question \n3)Complaint \n4)Other\n')
                # if (choice not in typeofchat):
                #     while (choice not in typeofchat):
                #         choice = raw_input('Please input a valid option. \n1)Comment \n2)Question \n3)Complaint \n4)Other\n')
                # chattopic = raw_input('What is the topic you would like to discuss today?\n')


## BELOW is Controller
host, port = '192.168.1.187', 8888
# host, port = 'localhost', 8888
client = Client(host, port)
client.do_send({'join': myname})

def periodic_poll():
    while 1:
        poll()
        sleep(0.05)  # seconds

thread = Thread(target=periodic_poll)
thread.daemon = True  # die when the main thread dies
thread.start()

while 1:
    mytxt = sys.stdin.readline().rstrip()
    if (topic_chosen_orAgent):
        if mytxt == ':e':
            print 'trolololololol'
        elif mytxt == ':s':
            pass
        elif mytxt.lower() == ':q':
            print('Now exiting!')
            client.do_send({u'speak': myname, u'txt': "User has left"})
            sys.exit()
        else:
            client.do_send({u'speak': myname, u'txt': mytxt})
    else:
        choice = raw_input('How may I help you today? \n1)Comment \n2)Question \n3)Complaint \n4)Other\n')
        if (choice not in typeofchat):
            while (choice not in typeofchat):
                choice = raw_input('Please input a valid option. \n1)Comment \n2)Question \n3)Complaint \n4)Other\n')
        chattopic = raw_input('What is the topic you would like to discuss today?\n')
        client.do_send({u'Need': typeofchat[choice], u'text': chattopic})
        topic_chosen_orAgent = True
