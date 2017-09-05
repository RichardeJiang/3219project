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
import json

# reload(sys)
# sys.setdefaultencoding('utf8')

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
	dirList = os.listdir('A00/')
	fileList = []
	for fileName in dirList:
		if fileName.endswith(".xml"):
			fileList.append(fileName)

	rootTag = "algorithm"

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

	d3nodeslist = []
	d3titlelist = []
	d3linklist = []
	dat = {}

	# graphCitation = graph()

	for fileName in fileList:
		try:
			DOMTree = xml.dom.minidom.parse('A00/' + fileName)
		except xml.parsers.expat.ExpatError, e:
			print "The file causing the error is: ", fileName
			print "The detailed error is: %s" %e

		collection = DOMTree.documentElement

		articles = collection.getElementsByTagName(rootTag)

		nodeName = ""
		nodeAuthor = "Unknown"

		### Notes about the raw text: <algorithm> is the article
		### each doc will have at most 3 <algorithm>s, the first is the note, second main article, third citations
		### Rule of thumb: use the title in the second <algorithm> as the node name; if no title, use the file name as the node name
		### then append the titles of the citations

		if len(articles) == 2:
			nodeName = fileName.split(".")[0]
		elif len(articles) == 3:
			nodeName = str(articles[1].getElementsByTagName("title")[0].firstChild.data.encode('utf-8'))
			authors = [str(i.firstChild.data.encode('utf-8')) for i in articles[1].getElementsByTagName("author")]
			nodeAuthor = ' and '.join(authors)
			# nodeName = str(articles[1].getElementsByTagName("title")[0].firstChild.data).decode('utf-8')

		currNode = nodeName + ' ' + str(nodeDate)
		d3nodeslist.append({'title': nodeName, 'authors': nodeAuthor, "type": "circle", "size": 60, "color": "#66CC33"})
		d3titlelist.append(nodeName)

		# graph.node(currNode)
		# print currNode
		# nodes.append(currNode)

		citations = articles[-1].getElementsByTagName("citation")

		# graphCitation = gv.Graph(format="svg")

		# citationStyle = {
		# 	'nodes': {
		# 		'fontname': 'Helvetica',
		# 		'shape': 'square',
		# 		'fontcolor': 'white',
		# 		'color': 'white',
		# 		'style': 'filled',
		# 		'fillcolor': '#dd0469',
		# 	}
		# }

		# graphCitation = apply_styles(graphCitation, citationStyle)

		for citation in citations:
			testFlag = citation.getAttribute("valid")
			if testFlag == "true":
				title = ""
				authors = "Unknown"
				if len(citation.getElementsByTagName("title")) < 1:
					title = str(citation.getElementsByTagName("rawString")[0].firstChild.data.encode('utf-8'))
				else:
					title = str(citation.getElementsByTagName("title")[0].firstChild.data.encode('utf-8'))
					# title.replace(",", "")
					if ", In" in title:
						title = title[:-4]

				date = nodeDate - 1
				if len(citation.getElementsByTagName("date")[0].childNodes) > 0:
					date = int(citation.getElementsByTagName("date")[0].childNodes[0].data)

				citationAuthors = [str(i.firstChild.data.encode('utf-8')) for i in citation.getElementsByTagName("author")]
				citationAuthorStr = ' and '.join(citationAuthors)

				currCitation = title + ' ' + str(date)
				if currCitation in citationNodes or currCitation in nodes:
					pass
				else:
					citationNodes.append(currCitation)
					# graphCitation.node(currCitation)

				if title in d3titlelist:
					pass
				else:
					d3nodeslist.append({'title': title, 'authors': citationAuthorStr, "type": "circle", "size": 40, "color": "#dd0469"})
					d3titlelist.append(title)


				# graph.subgraph(graphCitation)
				# graph.edge(currNode, currCitation)
				d3linklist.append({'source': d3titlelist.index(nodeName), 'target': d3titlelist.index(title)})


	dat = {"links": d3linklist, "nodes": d3nodeslist}
	with open('data.json', 'w') as f:
		json.dump(dat, f)
	# graph.render(filename='test')
	# graph.view(filename="test")

	pass