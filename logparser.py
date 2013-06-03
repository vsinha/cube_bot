import os, sys
from bulbs.neo4jserver import Graph
from markov import Markov

class LogParser():

	def __init__(self):
		self.sentences = []

	def stripMetadata(self, line):
		divider = line.find(": ")
		if divider == -1:
			return ""
		return line[divider+2:]

	def buildGraph(self):
		g = Graph()
		root = g.vertices.create(data="__END__")
		for i,sentence in enumerate(self.sentences):
	#		print(sentence)
			prev = root
			for currentWord in sentence:
				v = g.vertices.get_or_create("data",currentWord)
				g.edges.create(prev, "link", v)
				prev = v
				percent = (i*100./len(self.sentences))
				sys.stdout.write("\r%f%%" %percent)
			g.edges.create(prev, "link", root)

	def buildPickledDB(self):
		m = Markov()
		for i,sentence in enumerate(self.sentences):
			#print(str(i)+"/"+str(len(self.sentences)))
			percent = (i*100./len(self.sentences))
			sys.stdout.write("\r%f%%" %percent)
			sentence = m.removeItems(sentence)
			if sentence != []:
				m.addNewSentence(sentence)
			
		m.saveCache()

	def parse(self, file):
		f = open(file, 'r')
		for line in f.readlines():
			line = self.stripMetadata(line[0:-1])
			if (line == "") or ("has set the topic to:" in line):
				continue
			words = line.split(" ")
#			print(words)
			self.sentences.append(words)
		#self.buildGraph() # neo4j
		#self.buildPickledDB()


	def get_numlines(self):
		return self.numlines

if __name__ == '__main__':
	lp = LogParser()
	for root, dirs, files in os.walk("logs"):
		for file in files:
			lp.parse("logs/"+file)
	lp.buildGraph()
