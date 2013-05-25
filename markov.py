import logging
import random

from itertools import chain
from bulbs.neo4jserver import Graph
from graph import Key, Link
from wordpool import WordPool

class Markov (object):

	def __init__ (self, inputFile = None):
		self.g = Graph()
		self.g.add_proxy("key", Key)
		self.g.add_proxy("link", Link)

	def loadFile(self, inputFile):
		#for importing text from a file
		logging.info("Generating markov cache")

		self.inputFile = inputFile
		self.words = self.fileToWords()
		self.wordSize = len(self.words)
		logging.info("File has " + str(self.wordSize) + " words")

		self.storeToDB()

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
		#pick a random vertex
		print(len(self.g.V))
		randnum = random.randint(len(self.g.V))
		print(randnum)
		seed = self.g.vertices.get(randnum)
		print(seed)


	def clearDB(self):
		self.g.clear()

#for testing
if __name__ == '__main__':
	m = Markov()
	m.clearDB()
	sentences = []
	sentences.append("cube is a program")
	"""
	sentences.append("cube is a robot")
	sentences.append("cube is not a truck")
	sentences.append("a truck has wheels")
	"""
	for sentence in sentences:
		m.addNewSentence(sentence.split())
	m.generateText()
