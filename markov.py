import re

class Markov:

	def __init__ (self):
		pass

	markov = dict()

	def stripPunctuation (self, word):
		res = re.search('(^[.\!]*)(.*?)([.\!]*)$', word)
		print (res.group(1), res.group(2), res.group(3))
		return Word(res.group(1), res.group(2), res.group(3)) # begin punct, word, end punct

	def parseStringToDictionary (self, msg):
		wordList = list(map(self.stripPunctuation, msg.split()))
		for i in range(len(wordList) - 2):
			self.markov[(wordList[i], wordList[i+1])] = wordList[i+2]

	def printDictionary(self):
		for wordpair in self.markov.items():
			print (wordpair)

class Word ():

	def __init__ (self, prefix, word, postfix):
		self.prefix = prefix
		self.word = word
		self.postfix = postfix

	def __str__ (self):
		return (self.word(self.prefix) + self.word + self.postfix)

	def printword (self):
		return (self.word)

def main():
	m = Markov()
	m.parseStringToDictionary(".Portugal. the! ma'n? is a band.")
	m.printDictionary()
	
	
if __name__ == "__main__":
	main()
