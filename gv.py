from xml.dom.minidom import parse
import xml.dom.minidom
import re
import string
import sys
import os
import graphviz as gv

# g = gv.Graph(format="png")
# g.node('A')
# g.node('B')
# g.edge('A', 'B')
# g.render(filename="aaa")
import functools

reload(sys)
sys.setdefaultencoding('utf8')

graph = functools.partial(gv.Graph, format='svg')
digraph = functools.partial(gv.Digraph, format='svg')

def apply_styles(graph, styles):
	graph.graph_attr.update(
		('graph' in styles and styles['graph']) or {}
	)
	graph.node_attr.update(
		('nodes' in styles and styles['nodes']) or {}
	)
	graph.edge_attr.update(
		('edges' in styles and styles['edges']) or {}
	)
	return graph

def add_nodes(graph, nodes):
	for n in nodes:
		if isinstance(n, tuple):
			graph.node(n[0], **n[1])
		else:
			graph.node(n)
	return graph

def add_edges(graph, edges):
	for e in edges:
		if isinstance(e[0], tuple):
			graph.edge(*e[0], **e[1])
		else:
			graph.edge(*e)
	return graph

if __name__ == "__main__":
	count = 1
	result = ""
	dirList = os.listdir('A001/')
	fileList = []
	for fileName in dirList:
		if fileName.endswith(".xml"):
			fileList.append(fileName)

	rootTag = "algorithm"


	nodeName = ""
	nodeDate = 2000

	graph = gv.Graph(format="svg")
	styles = {
		'graph': {
			'label': 'A00',
			'fontsize': '14',
			'fontcolor': 'white',
			'bgcolor': '#333333',
			'rankdir': 'BT',
		},
		'nodes': {
			'fontname': 'Helvetica',
			'shape': 'hexagon',
			'fontcolor': 'white',
			'color': 'white',
			'style': 'filled',
			'fillcolor': '#006699',
		},
		'edges': {
			'style': 'dashed',
			'color': 'white',
			'arrowhead': 'open',
			'fontname': 'Courier',
			'fontsize': '12',
			'fontcolor': 'white',
		}
	}

	graph = apply_styles(graph, styles)

	nodes = []
	citationNodes = []

	# graphCitation = graph()

	for fileName in fileList:
		try:
			DOMTree = xml.dom.minidom.parse('A001/' + fileName)
		except xml.parsers.expat.ExpatError, e:
			print "The file causing the error is: ", fileName
			print "The detailed error is: %s" %e

		collection = DOMTree.documentElement

		articles = collection.getElementsByTagName(rootTag)

		### Notes about the raw text: <algorithm> is the article
		### each doc will have at most 3 <algorithm>s, the first is the note, second main article, third citations
		### Rule of thumb: use the title in the second <algorithm> as the node name; if no title, use the file name as the node name
		### then append the titles of the citations

		if len(articles) == 2:
			nodeName = fileName.split(".")[0]
		elif len(articles) == 3:
			nodeName = articles[1].getElementsByTagName("title")[0].firstChild.data.encode('utf-8')
			# nodeName = articles[1].getElementsByTagName("title")[0].firstChild.data.encode('ascii', 'ignore').decode('ascii')
			# nodeName = str(articles[1].getElementsByTagName("title")[0].firstChild.data).decode('utf-8')

		currNode = nodeName + ' ' + str(nodeDate)
		currNode = ''.join([i for i in currNode if not i.isdigit()])
		graph.node(currNode)
		print currNode
		nodes.append(currNode)

		citations = articles[-1].getElementsByTagName("citation")

		graphCitation = gv.Graph(format="svg")

		citationStyle = {
			'nodes': {
				'fontname': 'Helvetica',
				'shape': 'oval',
				'fontcolor': 'white',
				'color': 'white',
				'style': 'filled',
				'fillcolor': '#dd0469',
			}
		}

# fp.write(unicode(c['intro']).encode('utf-8'))
		graphCitation = apply_styles(graphCitation, citationStyle)

		for citation in citations:
			testFlag = citation.getAttribute("valid")
			if testFlag == "true":
				title = ""
				print len(citation.getElementsByTagName("title"))
				if len(citation.getElementsByTagName("title")) < 1:
					title = citation.getElementsByTagName("rawString")[0].firstChild.data.encode('utf-8')
					# title = citation.getElementsByTagName("rawString")[0].firstChild.data.encode('ascii', 'ignore').decode('ascii')
				else:
					title = citation.getElementsByTagName("title")[0].firstChild.data.encode('utf-8')
					# title = citation.getElementsByTagName("title")[0].firstChild.data.encode('ascii', 'ignore').decode('ascii')
					title.replace(",", "")
					if " In" in title:
						title = title[:-3]

				date = nodeDate - 1
				if len(citation.getElementsByTagName("date")[0].childNodes) > 0:
					date = int(citation.getElementsByTagName("date")[0].childNodes[0].data)

				currCitation = title + ' ' + str(date)
				if currCitation in citationNodes or currCitation in nodes:
					pass
				else:
					currCitation = ''.join([i for i in currCitation if not i.isdigit()])
					citationNodes.append(currCitation)

					graphCitation.node(currCitation)


				# graphCitation.graph_attr['rank']='same'
				graphCitation.rankdir='TB';
				graph.subgraph(graphCitation)
				# graphCitation.graph_attr['rank']='same'
				graph.edge(currNode, currCitation)


	graph.rankdir = 'LR';
	graph.render(filename='test')
	# graph.view(filename="test")

	pass