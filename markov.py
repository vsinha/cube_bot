import atexit
import logging
import pickle
import random


			


class Markov (object):

	def __init__ (self, inputFile):
		try: 
			self.cache = pickle.load( open("save.p", "rb") )
		except:
			self.cache = {}

		self.counter = 0 #keep track of how many new entries to the db there have been

		"""
		#for importing text from a file
		logging.info("Generating markov cache")

		self.inputFile = inputFile
		self.words = self.fileToWords()
		self.wordSize = len(self.words)
		logging.info("File has " + str(self.wordSize) + " words")

		self.database()
		"""

		atexit.register(self.saveCache)

	def saveCache(self):
		logging.info("saving cache")
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

		#save the cache every n messages
		n = 20
		self.counter += 1
		if self.counter % n == 0:
			self.saveCache()

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


