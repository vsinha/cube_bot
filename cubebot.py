import configparser
import logging
import random
import re
import string
import sleekxmpp
import sys

from cube_bot import Markov

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

	"""
	some utility functions to process the message text
	"""
	def removeItems(self, message):
		#do all the operations!
		message = self.removeParens(message)
		message = self.removeAsteriskWords(message)
		message = self.removeUsernames(message)
		return message

	def removeParens(message):
		message = re.sub('[\(\)\{\}<>]', '', message)
		return message

	def removeUsernames(message):
		#if the first word is a username (ie, ends in ':'), remove it
		if message[0].endswith(':'):
			message.remove(message[0])
		return message

	def removeAsteriskWords(message):
		#users correct typos with *word or word* generally
		#we don't want cube repeating those
		#TODO add a spellchecker so cube can exhibit this behavior correctly
		if len(message.split()) == 1: #one word
			if message.find('*') != 1: #with an asterisk
				#return an empty string
				return ""

	def botNickInText(self, message):
		#strip punctuation from message_body
		regex = re.compile('[%s]' % re.escape(string.punctuation))
		message_no_punct = []
		for word in message:
		 	message_no_punct.append(regex.sub('', word).lower())

		return self.nick in message_no_punct

	
 	#parse incoming messages
	def messageHandler(self, msg):

		#preprocess input
		human_nick = msg['mucnick'] # whoever we're responding to
		response = "beep boop" #initialize response

		original_message_body = msg['body'].split()
		message_body = self.removeItems(original_message_body)

		if len(message_body.split()) == 0:
			#message is empty, exit now and save ourselves the trouble
			return

		#always make sure the message we're replying to didn't come from self
		if human_nick != self.nick:

			#reply if username is mentioned
			if self.botNickInText(original_message_body):
				response = self.markov.generateText()

			#reply if animal sounds are mentioned
			elif any( word in animalsounds_set for word in message_body ):
				response = random.choice(animalsounds)

			else:
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
