import logging
import random

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

	def tripletGenerator(self):
		#starts at the first word and goes forward
		if len(self.words) < 3:
			return

		for i in range(len(self.words) - 2):
			#generator, so we're independent of input file size
			triplet = [self.words[i], self.words[i+1], self.words[i+2]]
			yield triplet

	def storeToDatabase(self):
		#initialize with empty string, which we know already exists in the db
		last = '__ROOT__' 
		lastVertex = self.g.vertices.index.lookup(data = last)
		#^this has to return a list of size 1, every time
		print("lastVertex: ", lastVertex)

		#store triplet, and connect with previously stored one
		for triplet in self.tripletGenerator():
			current = ' '.join(triplet) #saving entries as strings (for now)
			print("last: ", last)
			print("current: ", current)
			#if our previous string exists already, we need to append
			lookup = self.g.vertices.index.lookup(data=last) #returns generator
			try:
				lookup = list(lookup) #convert generator to list
			except TypeError: #lookup is empty
				pass

			print("lookup: ", lookup)
			currentVertex = self.g.vertices.create(data = current)

			if len(lookup) != 0: #this exists already
				#so link with results of lookup
				self.g.edges.create(lookup[0], "link", currentVertex)
			else:
				#otherwise, link with whatever we just created
				self.g.edges.create(lastVertex, "link", currentVertex)
			last = current
			lastVertex = currentVertex

	def generateText(self):
		#pick a random vertex
		randnum = random.randint(1, len(self.g.V))
		seed = self.g.vertices.get(randnum)
		print(seed)

	def resetDB(self):
		self.g.clear()
		self.g.vertices.create(data = '__ROOT__') #initialize w/ empty string node

#for testing
if __name__ == '__main__':
	m = Markov()
	m.resetDB()
	sentences = []
	sentences.append("cube is a program")
	sentences.append("cube is a robot")
	sentences.append("cube is not a truck")
	sentences.append("a truck has wheels")
	for sentence in sentences:
		m.addNewSentence(sentence.split())
	m.generateText()
