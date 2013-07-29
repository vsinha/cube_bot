import atexit
import logging
import pickle
import random

from itertools import chain
#from wordpool import WordPool

cacheFfile = "save_forward.p" 
cacheRfile = "save_reverse.p"

class Markov (object):

	def __init__ (self, inputFile = None):
		try: 
			logging.info("Loading cache")
			self.cacheF = pickle.load( open(cacheFfile, "rb") )
			self.cacheR = pickle.load( open(cacheRfile, "rb") )
		except:
			logging.info("No cache found, creating a new one")
			self.cacheF = {}
			self.cacheR = {}

		self.counter = 0 #keep track of new entries to the db 
		atexit.register(self.saveCache) #initialize saving at exit

	#TODO get this to read chat log files (either plaintext or html)
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

	#appends and prepends special tokens
	def sentenceToWords(self, words):
		if words[0] != '__END__': words.insert(0, '__END__') #prepend special word
		if words[-1] != '__END__': words.append('__END__') #and append
		return words

	#preprocesses the sentence (adds end tokens), and calls storeToDB()
	def addNewSentence(self, sentence):
		if len(sentence) != 0:
			logging.info("ADDING: " + ' '.join(sentence))
			self.words = self.sentenceToWords(sentence)
			self.storeToDB()

		#save the cache every n messages
		#TODO this doesn't do anything because pickle needs help with tuples
		n = 20
		self.counter += 1
		if self.counter % n == 0:
			self.saveCache()
			self.counter = 0 #reset the counter

	def saveCache(self):
		logging.info("SAVING caches")
		pickle.dump(self.cacheF, open(cacheFfile, "wb"))
		pickle.dump(self.cacheR, open(cacheRfile, "wb"))

	"""
	triplet generators slice the sentence into triplets
	example: "the quick brown fox jumps" becomes:
	"the quick" -> "brown"
	"quick brown" -> "fox"
	"brown fox" -> "jumps"

	these are returned using yield(), which turns the function into
	a generator, and lazy loads the list rather than creating it all at once
	
	one goes forward, and one goes backwards ("jumps fox" -> brown) because
	we want to be able to generate markov chains in both directions, and thus
	have to store 2 separate dicts.

	storeToDB() calls database twice, passing in each generator and cache
	"""
	#TODO ditch this dict stuff and use an actual database

	#starts at the first word and goes forward
	def forwardTripletGenerator(self):
		if len(self.words) < 3:
			return

		for i in range(len(self.words) - 2):
			#generator, so we're independent of input file size
			yield (self.words[i], self.words[i+1], self.words[i+2])
	
	#do the same thing as above, but from the end of the string
	def reverseTripletGenerator(self):
		if len(self.words) < 3:
			return

		i = len(self.words) - 1 #index of last word, and goes backwards
		while i >= 2:
			yield (self.words[i], self.words[i-1], self.words[i-2])
			i -= 1

	#store markov chains based on which tripletGenerator we get handed
	def database(self, tripletGenerator, cache):
		for w1, w2, w3 in tripletGenerator:
			#use a namedtuple for easy generating later
			key = ' '.join([w1, w2])
			if key in cache: #if we've already seen this key pair
				cache[key].append(w3)
			else:
				cache[key] = [w3]

	#generate markov chains in both directions
	#by calling database with both triplet generators
	def storeToDB(self):
		self.database(self.forwardTripletGenerator(), self.cacheF)
		self.database(self.reverseTripletGenerator(), self.cacheR)

	"""
	To generate text, we:
		pick a seed key (2 words)
		generate text forwards and append
		generate text backwards and prepend (flipping the order of the words)
		return the completed sentence

	generateText calls gen() twice (forwards and backwards)
	then calls stripTokens() to get rid of __END__
	stripTokens() also turns the list of words into a space-separated string
	"""
	def generateText(self):
		response = []

		#start with a random word
		#TODO add wordpool ring buffer functionality
		seed = random.choice(list(self.cacheF.keys()))
		seedw1 = seed.split()[0]
		seedw2 = seed.split()[1]

		response.append(self.gen(seedw1, seedw2, self.cacheF))
		#we're left with [["word", "word2"]], this removes the outer brakets
		response = list(chain.from_iterable(response))
		#delete first two words from response because these are the key
		del response[0:2] 

		second_half = self.gen(seedw2, seedw1, self.cacheR)
		for word in second_half:
			response.insert(0, word)

		response = self.stripTokens(response)
		return response

	#generate text using whichever cache is given
	def gen(self, w1, w2, cache):
		output = []
		while True:
			output.append(w1)
			#print(w1, w2, output)
			try:
				w1, w2 = w2, random.choice(cache[(w1 + ' ' + w2)])
			except KeyError:
				#we've looked up a pair where the value is __END__
				#print("keyError", w1, w2)
				output.append(w2)
				return output

	#remove end tokens and make the list of words into a string
	def stripTokens(self, response):
		sentence = [w for w in response if w != '__END__']
		return ' '.join(sentence)

#for testing
if __name__ == '__main__':
	m = Markov()
	ss = [] #ss = sentences

	"""
	#one set of test sentences
	ss.append("cube is a program")
	ss.append("cube is a robot")
	ss.append("cube is not a truck")
	ss.append("a truck has wheels")
	ss.append("a truck is not a cube")
	"""

	#and another set
	ss.append("this is a test")
	ss.append("this is another test")
	ss.append("another test would help")
	ss.append("pudi pudi pudi")

	for s in ss: #s = sentence
		m.addNewSentence(s.split())
	r = m.generateText() #r = response
	print(r)
