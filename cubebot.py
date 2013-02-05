import getpass
import logging
import configparser
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

questions = ["hmmm?", "yes?", "what?"]

pronouns = ["who", "who's", "what", "what's"]
pronouns_set = set(pronouns)

greetingwords = ["greetings", "hey", "hi", "hello", "sup", "yo", "hi there"]
greetingwords_set = set(greetingwords)

swearwords = ["fuck", "suck"] #don't want cube being bullied
swearwords_set = set(swearwords)

passive_responses = ["reminisces about vietnam", "writes a gui using visual basic", "goes outside... just kidding"]


class CubeBot (sleekxmpp.ClientXMPP):

	def __init__ (self, jid, password, room, nick):
		sleekxmpp.ClientXMPP.__init__(self, jid, password)
		self.room = room
		self.nick = nick
		self.add_event_handler("session_start", self.start) 
		self.add_event_handler("groupchat_message", self.bot_message)

	#begin receiving/responding
	def start(self, event):
		self.get_roster()
		self.send_presence()
		self.plugin['xep_0045'].joinMUC(self.room, self.nick) #enable group chat

 	#parse incoming messages
	def bot_message(self, msg):

		#preprocess input
		message_body = [x.lower() for x in msg['body'].split()] 
		human_nick = msg['mucnick'] # whoever we're responding to

		#reply if username is mentioned
		#always make sure the message we're replying to didn't come from self
		if human_nick != self.nick and self.nick in message_body:

			if len(message_body) == 1: #self.nick is the only word!
				response = random.choice(questions)

			elif any( word in pronouns_set for word in message_body ): #introduce yourself
				response = "/me is a chat bot"

			elif any( word in greetingwords_set for word in message_body ):
				response = random.choice(greetingwords) + ", " + human_nick

			elif any( word in swearwords_set for word in message_body ):
				response = human_nick + ", your mother is a whore"

			else:
				response = "/me " + random.choice(passive_responses)
			
			#send finished response
			self.send_message(mto=msg['from'].bare, mbody=response, mtype='groupchat')



if __name__ == '__main__':

	#read config file
	config = configparser.ConfigParser()
	config.read('config.conf')

	jid 	= config.get('cube', 'jid')
	pw 		= config.get('cube', 'password')
	server 	= config.get('cube', 'server')
	nick 	= config.get('cube', 'nick')

	#setup logging
	logging.basicConfig(level=logging.INFO,
						format='%(levelname)-8s %(message)s')

    # Setup the bot and register plugins.
	xmpp = CubeBot(jid, pw, server, nick)
	xmpp.register_plugin('xep_0030') # Service Discovery
	xmpp.register_plugin('xep_0045') # Multi-User Chat
	xmpp.register_plugin('xep_0199') # XMPP Ping

    # Connect to the XMPP server and start processing XMPP stanzas.
	if xmpp.connect(('obnauticus.com', 5222)):
		xmpp.process(block=True)
		print("Done")
	else:
		print("Unable to connect.")
