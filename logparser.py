import os
from bulbs.neo4jserver import Graph
from graph import Key, Link

class LogParser():

	def __init__(self):
		g = Graph()
		self.sentences = []

	def stripMetadata(self, line):
		divider = line.find(": ")
		if divider == -1:
			return ""
		return line[divider+2:]

	def buildGraph(self):
		root = g.vertices.create(token="__END__")
		


	def parse(self, file):
		f = open(file, 'r')
		for line in f.readlines():
			line = self.stripMetadata(line[0:-1])
			if line == "":
				continue
			words = line.split(" ")
			self.sentences.append(words)
		buildGraph(sentences)

	def get_numlines(self):
		return self.numlines

if __name__ == '__main__':
	lp = LogParser()
	for root, dirs, files in os.walk("logs"):
		for file in files:
			lp.parse("logs/"+file)
