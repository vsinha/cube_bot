import atexit
import configparser
import logging
import pickle
import random
import sleekxmpp
import sys

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

		#always make sure the message we're replying to didn't come from self
		if human_nick != self.nick:


			#reply if username is mentioned
			if self.nick in message_body:

				response = self.markov.generateText()
				#self.nick is the only word, respond with a random question
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
			elif message_body[0][0] == '#':
				response = "/topic " + ' '.join(message_body)

			else:
				self.markov.addNewSentence(message_body)

			#send finished response if it's been modified
			if response != "beep boop":
				self.send_message(mto=msg['from'].bare, mbody=response, mtype='groupchat')
				logging.info("REPLY: " + response)


class Markov(object):

	def __init__ (self, inputFile):
		try: 
			self.cache = pickle.load( open("save.p", "rb") )
		except:
			self.cache = {}

		"""logging.info("Generating markov cache")

		self.inputFile = inputFile
		self.words = self.fileToWords()
		self.wordSize = len(self.words)
		logging.info("File has " + str(self.wordSize) + " words")

		self.database()
		"""

		atexit.register(self.saveCache)

	def saveCache(self):
		pickle.dump(self.cache, open("save.p", "wb"))

	def fileToWords(self):
		self.inputFile.seek(0)
		data = self.inputFile.read()
		words = data.lower().split()
		return words

	def sentenceToWords(self, words):
		words.insert(0, '__FIRST__') #prepend special word
		words.append('__END__') #and append
		return words

	def addNewSentence(self, sentence):
		logging.info("adding new sentence: " + ' '.join(sentence))
		self.words = self.sentenceToWords(sentence)
		self.wordSize = len(self.cache) #our cache grows as we add sentences
		self.database()


	def tripletGenerator(self):
		if len(self.words) < 3:
			return

		for i in range(len(self.words) - 2):
			#generator, so we're independent of input file size
			yield (self.words[i], self.words[i+1], self.words[i+2])
	
	def database(self):
		for w1, w2, w3 in self.tripletGenerator():
			key = (w1, w2)
			if key in self.cache: #if we've already seen this key pair
				self.cache[key].append(w3)
			else:
				self.cache[key] = [w3]

	def generateText(self, size = 25):

		firstFlag = ' '
		while firstFlag != '__FIRST__':
			startwords = random.choice(list(self.cache.keys()))
			firstFlag, w1 = startwords
		w2list = random.choice(self.cache[(firstFlag, w1)]) # make sure we always pick an appropriate starting place		
		w2 = ''.join(w2list)
			
		#print (w1 + ", " + w2)
		outputWords = []

		while True:
			outputWords.append(w1)
			try:
				w1, w2 = w2, random.choice(self.cache[(w1, w2)])
			except KeyError:
				#we've looked up a pair where the second word is __END__
				return ' '.join(outputWords) #don't append the same word twice

			#print (w1 + ", " + w2)
			if w2 == '__END__':
				outputWords.append(w1)
				return ' '.join(outputWords)


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
