#I knew there was a name for this thing!
#it's a ring buffer

class WordPool (object):
	#we're keeping a list of recently used words

	def __init__(self, poolsize):
		self.poolsize = poolsize
		self.i = 0
		self.pool = [] 

	def addSentence(self, sentence):
		for word in sentence:
			print("adding: " + word)
			if len(self.pool) < self.poolsize:
				#fill the list until it's at the right size
				self.pool.append(word)
			else:
				self.pool[self.i] = word
				self.i += 1
				if self.i >= self.poolsize:
					self.i = 0
	
#for testing
if __name__ == "__main__":
	recent = WordPool(4)
	sentence = "this is four words"
	sentence = sentence.split()

	recent.addSentence(sentence)
	print(recent.pool)
	recent.addSentence("1".split())
	print(recent.pool)
	recent.addSentence("2".split())
	print(recent.pool)
	recent.addSentence("3".split())
	print(recent.pool)
	recent.addSentence("4".split())
	print(recent.pool)
	recent.addSentence("test".split())
	print(recent.pool)
