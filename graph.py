from bulbs.model import Node, Relationship
from bulbs.property import String
from bulbs.neo4jserver import Graph

class Key(Node):
	element_type = "key"
	#store triplet
	data = String()

class Link(Relationship):
	label = "link"

"""
this tripletGenerator is for testing only!!!!
everything below this comment is for testing
"""
def tripletGenerator():
	#starts at the first word and goes forward
	if len(s) < 3:
		return

	for i in range(len(s) - 2):
		#generator, so we're independent of input file size
		words = [s[i], s[i+1], s[i+2]]
		yield words

sen = "END this is a sentence END"
s = sen.split()

if __name__ == '__main__':
	g = Graph()
	g.clear()
	g.add_proxy("key", Key)
	g.add_proxy("link", Link)

	print(s)

	prev = ''
	prevg = g.vertices.create(data=prev)
	for words in tripletGenerator():
		curr = ' '.join(words)
		print(curr)
		currg = g.vertices.create(data=curr)
		g.edges.create(prevg, "link", currg)
		prevg = currg
