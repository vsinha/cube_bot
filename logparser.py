import os, re

class LogParser():


	def __init__ (self):
		self.numlines = 0

	def stripMetadata(self, line):
		divider = line.find(": ")
		if divider == -1:
			return ""
		return line[divider+2:]


	def parse(self, file):
		f = open(file, 'r')
		for line in f.readlines():
			line = self.stripMetadata(line[0:-1])
			self.numlines += 1

	def get_numlines(self):
		return self.numlines

if __name__ == '__main__':
	lp = LogParser()
	for root, dirs, files in os.walk("logs"):
		for file in files:
			lp.parse("logs/"+file)
	print(lp.get_numlines())
