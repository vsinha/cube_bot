import configparser
import logging
import random
import re
import string
import sleekxmpp
import sys

from cube_bot import Markov
from cube_bot import WordPool

# ensure unicode is handled properly incase python is not v3.0
if sys.version_info < (3, 0):
	reload(sys)
	sys.setdefaultencoding('utf8')
else:
	raw_input = input

animalsounds = ["meow", "woof", "moo"]
animalsounds_set = set(animalsounds)

class CubeBot (sleekxmpp.ClientXMPP):

	def __init__ (self, jid, password, room, nick, fileName):
		sleekxmpp.ClientXMPP.__init__(self, jid, password)
		self.room = room
		self.nick = nick

		#initialize markov chain with input file
		inputFile = open(fileName)
		self.markov = Markov(inputFile)

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
		message_body = msg['body'].split()
		human_nick = msg['mucnick'] # whoever we're responding to
		response = "beep boop" #initialize response

		#strip punctuation from message_body
		regex = re.compile('[%s]' % re.escape(string.punctuation))
		message_no_punct = []
		for word in message_body:
		 	message_no_punct.append(regex.sub('', word).lower())

		#always make sure the message we're replying to didn't come from self
		if human_nick != self.nick:

			#reply if username is mentioned
			if self.nick in message_no_punct:

				response = self.markov.generateText()

				"""
				if len(message_body) == 1:
					pass

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
					"""

			#reply if animal sounds are mentioned
			elif any( word in animalsounds_set for word in message_body ):
				response = random.choice(animalsounds)

			#change the topic if message starts with #
			#TODO: this doesn't work for some reason
			elif message_body[0][0] == '#':
				response = "/topic " + ' '.join(message_body)

			else:
				#if the first word is a username (ie, ends in ':') remove it before adding
				if message_body[0].endswith(':'):
					message_body.remove(message_body[0])

				self.markov.addNewSentence(message_body)

			#send finished response if it's been modified
			if response != "beep boop":
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
	fileName = config.get('cube', 'textFileName')

	#setup logging
	logging.basicConfig(level=logging.INFO, format='%(levelname)-8s %(message)s')

    # Setup the bot and register plugins.
	xmpp = CubeBot(jid, pw, server, nick, fileName)
	xmpp.register_plugin('xep_0030') # Service Discovery
	xmpp.register_plugin('xep_0045') # Multi-User Chat
	xmpp.register_plugin('xep_0199') # XMPP Ping



    # Connect to the XMPP server and start processing XMPP stanzas.
	if xmpp.connect(('obnauticus.com', 5222)):
		xmpp.process(block=True)
		print("Done")
	else:
		print("Unable to connect.")
