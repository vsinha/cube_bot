import getpass
import logging
from optparse import OptionParser
import operator
import random
import sleekxmpp
import sys

# ensure unicode is handled properly incase python is not v3.0
if sys.version_info < (3, 0):
	reload(sys)
	sys.setdefaultencoding('utf8')
else:
	raw_input = input


greetingwords = ["greetings", "hey", "hi", "hello", "sup", "yo", "hi there"]
greetingwords_set = set(greetingwords)

swearwords = ["fuck", "suck"] #don't want cube being bullied
swearwords_set = set(swearwords)


class MUCBot (sleekxmpp.ClientXMPP):

	def __init__ (self, jid, password, room, nick):
		sleekxmpp.ClientXMPP.__init__(self, jid, password)
		self.room = room
		self.nick = nick
		self.add_event_handler("session_start", self.start) #begin receiving/responding
		self.add_event_handler("groupchat_message", self.bot_message)  
	
	def start(self, event):
		self.get_roster()
		self.send_presence()
		self.plugin['xep_0045'].joinMUC(self.room, self.nick) #enable group chat


	def bot_message(self, msg):
		#reply if username is mentioned
		#always make sure the message we're replying to didn't come from self

		#convert all input to lowercase
		message_body = [x.lower() for x in msg['body'].split()] 
		human_nick = msg['mucnick'] # whoever we're responding to

		if human_nick != self.nick and self.nick in message_body:

			if any( word in greetingwords_set for word in message_body ):
				response = random.choice(greetingwords) + ", " + human_nick

			if any( word in swearwords_set for word in message_body):
				response = human_nick + ", your mother is a whore"

			self.send_message(mto=msg['from'].bare, mbody=response, mtype='groupchat')

# TODO
# fuck off cube
# <user>, your <noun> is a <noun>


if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    # Setup the MUCBot and register plugins.
    xmpp = MUCBot("cube@obnauticus.com", "chickentender23", "#emc2@conference.obnauticus.com", "cube")
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0045') # Multi-User Chat
    xmpp.register_plugin('xep_0199') # XMPP Ping

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect(('obnauticus.com', 5222)):
        xmpp.process(block=True)
        print("Done")
    else:
        print("Unable to connect.")
