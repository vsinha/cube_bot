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
pronouns_set = set(pronouns) #sets are faster for 'x in s'

greetingwords = ["greetings", "hey", "hi", "hello", "sup", "yo", "hi there"]
greetingwords_set = set(greetingwords)

swearwords = ["suck", "bitch", "fuck"] #don't want cube being bullied
swearwords_set = set(swearwords)

animalsounds = ["meow", "woof", "moo"]
animalsounds_set = set(animalsounds)

passive_responses = ["reminisces about vietnam", "writes a gui using visual basic", "goes outside... just kidding"]


class CubeBot (sleekxmpp.ClientXMPP):

	def __init__ (self, jid, password, room, nick):
		sleekxmpp.ClientXMPP.__init__(self, jid, password)
		self.room = room
		self.nick = nick
		self.add_event_handler("session_start", self.start) 
		self.add_event_handler("groupchat_message", self.messageHandler)

	#begin receiving/responding
	def start(self, event):
		self.get_roster()
		self.send_presence()
		self.plugin['xep_0045'].joinMUC(self.room, self.nick) #enable group chat

 	#parse incoming messages
	def messageHandler(self, msg):

		#preprocess input
		message_body = [x.lower() for x in msg['body'].split()] 
		human_nick = msg['mucnick'] # whoever we're responding to
		response = "bleep bloop" #initialize response

		#always make sure the message we're replying to didn't come from self
		if human_nick != self.nick:

			#reply if username is mentioned
			if self.nick in message_body:

				#self.nick is the only word, respond with a random question
				if len(message_body) == 1: 
					response = random.choice(questions)

				#who are you?
				elif any( word in pronouns_set for word in message_body ): 
					response = "/me is a chat bot"

				#say hello
				elif any( word in greetingwords_set for word in message_body ):
					response = random.choice(greetingwords) + ", " + human_nick

				#get angry
				elif any( word in swearwords_set for word in message_body ):
					response = human_nick + ", your mother is a whore"

				#pretend to be doing something
				else:
					response = "/me " + random.choice(passive_responses)

				#send finished response
				self.send_message(mto=msg['from'].bare, mbody=response, mtype='groupchat')
				logging.info("REPLY: " + response)

			#reply if animal sounds are mentioned
			if any( word in animalsounds_set for word in message_body ):
				response = random.choice(animalsounds)
				
				#send finished response
				self.send_message(mto=msg['from'].bare, mbody=response, mtype='groupchat')
				logging.info("REPLY: " + response)



if __name__ == '__main__': 

	#read config file
	config = configparser.ConfigParser()
	config.read('config.conf')

	jid 	= config.get('cube', 'jid')
	pw 		= config.get('cube', 'password')
	server 	= config.get('cube', 'server')
	nick 	= config.get('cube', 'nick')

	#setup logging
	logging.basicConfig(level=logging.INFO, format='%(levelname)-8s %(message)s')

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
