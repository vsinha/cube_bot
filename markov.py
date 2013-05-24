import atexit
import logging
import json
import random

from collections import namedtuple
from itertools import chain
from bulbs.neo4jserver import Graph
from graph import Key, Link
from wordpool import WordPool

cacheFfile = "saveforward.json" 
cacheRfile = "savereverse.json"

class Markov (object):

	def __init__ (self, inputFile = None):
		self.g = Graph()
		self.g.add_proxy("key", Key)
		self.g.add_proxy("link", Link)

		try: 
			logging.info("Loading cache")
			self.cacheF = json.load( open(cacheFfile, "r") )
			self.cacheR = json.load( open(cacheRfile, "r") )
		except:
			logging.info("No cache found, creating a new one")
			self.cacheF = {}
			self.cacheR = {}

		
		self.Key = namedtuple("Key", ["key1", "key2"])
		self.counter = 0 #keep track of new entries to the db 
		atexit.register(self.saveCache) #initialize saving at exit

	def loadFile(self, inputFile):
		#for importing text from a file
		logging.info("Generating markov cache")

		self.inputFile = inputFile
		self.words = self.fileToWords()
		self.wordSize = len(self.words)
		logging.info("File has " + str(self.wordSize) + " words")

		self.storeToDB()

	def saveCache(self):
		logging.info("Saving cache(s)")
		json.dump(self.cacheF, open(cacheFfile, "w"))
		json.dump(self.cacheR, open(cacheRfile, "w"))

	def fileToWords(self):
		self.inputFile.seek(0)
		data = self.inputFile.read()
		words = data.lower().split()
		return words

	def sentenceToWords(self, words):
		words.insert(0, '__END__') #prepend special word
		words.append('__END__') #and append
		return words

	def addNewSentence(self, sentence):
		logging.info("adding new sentence: " + ' '.join(sentence))
		self.words = self.sentenceToWords(sentence)
		self.storeToDatabase()

		#save the cache every n messages
		n = 20
		self.counter += 1
		if self.counter % n == 0:
			self.saveCache()
			self.counter = 0 #reset the counter

	def tripletGenerator(self):
		#starts at the first word and goes forward
		if len(self.words) < 3:
			return

		for i in range(len(self.words) - 2):
			#generator, so we're independent of input file size
			triplet = [self.words[i], self.words[i+1], self.words[i+2]]
			yield triplet

	def storeToDatabase(self):
		last = ''
		lastVertex = self.g.vertices.create(data = last)

		#store triplet, and connect with previously stored one
		for triplet in self.tripletGenerator():
			current = ' '.join(triplet) #saving entries as strings (for now)
			print(current)
			currentVertex = self.g.vertices.create(data = current)
			self.g.edges.create(lastVertex, "link", currentVertex)
			lastVertex = currentVertex

	def generateText(self):
		seedword = '__END__' #initialize wrong so we can enter the while loop
		response = []

		while seedword == '__END__':
			choice = random.choice(list(self.cacheF.keys()))
			seedword = choice.key1
			keyF = choice.key2

		response.append(self.gen(seedword, keyF, self.cacheF))
		response = list(chain.from_iterable(response))
		response.pop(0)

		#needs to pick a key2 where key1 is our seedword
		keys = self.cacheR.keys()
		choices = [key for key in keys if key.key1==seedword]
		if len(choices) == 0: #we're at the first word already
			pass
		else:
			choice = random.choice(choices)
			keyR = choice.key2
			second_half = self.gen(seedword, keyR, self.cacheR)
			for word in second_half:
				response.insert(0, word)

			print(response)


	def gen(self, w1, w2, cache):
		output = []
		while True:
			output.append(w1)
			#print(w1, w2, output)
			try:
				w1, w2 = w2, random.choice(cache[(w1, w2)])
			except KeyError:
				#we've looked up a pair where the value is __END__
				#print("keyError", w1, w2)
				output.append(w2)
				return output

			"""
			if w2 == '__END__':
				output.append(w1)
				return output
			"""

if __name__ == '__main__':
	m = Markov()
	sentences = []
	sentences.append("cube is a program")
	sentences.append("cube is a robot")
	sentences.append("cube is not a truck")
	sentences.append("a truck has wheels")
	for sentence in sentences:
		m.addNewSentence(sentence.split())
	#m.generateText()
