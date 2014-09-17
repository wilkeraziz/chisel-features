#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from client import client
import logging
import json

#dict(map(lambda x: zip(x.values()[0]['govIndex'],x.values()[0]['depIndex'])[0],a))

class Negation:

	def __init__(self):
		pass

	def get_dependencies(self,string,lang):
		deps = client({'sentence':string,'lang':lang})
		unpackedDeps = json.loads(json.loads(deps)['result'])
		#TODO:the lexical elements are to be decoded in utf-8
		return unpackedDeps

	def score_deps(self,sentDeps1,sentDeps2):

		deps1,deps2 = sentDeps1['deps'],sentDeps2['deps']
		govDepIndeces1,govDepIndeces2 = sentDeps1['govDepIndeces'],sentDeps2['govDepIndeces']
		depLexical1,depLexical2 = sentDeps1['depLexical'],sentDeps2['depLexical']


		negDeps1 = filter(lambda x: x.keys()[0]=='neg',deps1)
		negDeps2 = filter(lambda x: x.keys()[0]=='neg',deps2)
		negCues1,negCues2 = self.extractCues(negDeps1,negDeps2)
		# logging.info('negCues1')
		# logging.info(negCues1)
		# logging.info('negCues2')
		# logging.info(negCues2)
		negEvents1,negEvents2 = self.extractEvents(negDeps1,negDeps2)
		# logging.info('negEvents1')
		# logging.info(negEvents1)
		# logging.info('negEvents2')
		# logging.info(negEvents2)
		scopes = self.extractScope([(negDeps1,govDepIndeces1,depLexical1),(negDeps2,govDepIndeces2,depLexical2)])


		cueScore = self.scoreFmeasure(negCues1,negCues2)
		# logging.info(cueScore)
		eventScore = self.scoreFmeasure(negEvents1,negEvents2)
		# logging.info(eventScore)
		scopeScore = self.scoreScopeOverlap(None,None)

	def extractCues(self,negDeps1,negDeps2):
		negCues1 = map(lambda x: x['neg']['dep'],negDeps1) if negDeps1!=[] else []
		negCues2 = map(lambda x: x['neg']['dep'],negDeps2) if negDeps2!=[] else []

		return negCues1,negCues2

	def extractEvents(self,negDeps1,negDeps2):
		negEvents1 = map(lambda x: x['neg']['gov'],negDeps1) if negDeps1!=[] else []
		negEvents2 = map(lambda x: x['neg']['gov'],negDeps2) if negDeps2!=[] else []
		#plug HERE translation probabilties if langs are different

		return negEvents1,negEvents2

	def extractScope(self,args):
		#Extracting a dictionary of gov-dep indeces
		scopes = []
		for sentDepInfo in args:
			negDeps = sentDepInfo[0]
			govDepIndeces = sentDepInfo[1]
			depLexical = sentDepInfo[2]
		    #getting the mapping of gov indeces to dep indeces
			logging.info(govDepIndeces)
			#there can be multiple negations
			negIndeces = map(lambda x: x['neg']['depIndex'],negDeps)
			print negIndeces
			if negIndeces == []: scopes.append(scope)
			else:
				govIndeces = [x for x,y in govDepIndeces.items() if set(negIndeces).intersection(set(y))!=set([])]
				scopes = self.getWordsInScope(negIndeces,govIndeces,govDepIndeces,depLexical)

		return scopes

	def getWordsInScope(self,negIndeces,govIndeces,govDepIndeces,depLexical):
		
		scopes = []

		for govIndex in govIndeces:
			indecesToRetrieve = [govIndex]
			currentList = [govIndex]
			while currentList!=[]:
				currentIndex = currentList.pop()
				if govDepIndeces.has_key(currentIndex):
					currentList.extend(govDepIndeces[currentIndex])
					indecesToRetrieve.extend(govDepIndeces[currentIndex])
			indecesToRetrieve = filter(lambda x: x not in negIndeces,indecesToRetrieve)
			lexElements = map(lambda x: depLexical[str(x)],sorted(map(lambda x: int(x),indecesToRetrieve)))
			scopes.append(lexElements)

		return scopes

	def scoreFmeasure(self,hyp,ref):

		try:
			precision = len(filter(lambda x: x[0]==x[1],zip(hyp,ref)))/len(hyp)
		except ZeroDivisionError:
			precision = 0.0
		# logging.info(precision)
		try:
			recall = len(filter(lambda x: x[0]==x[1],zip(hyp,ref)))/len(ref)
		except ZeroDivisionError:
			recall = 0.0
		# logging.info(recall)
		fMeasure = (precision + recall) / 2 
		return fMeasure

	def scoreScopeOverlap(self,scope1,scope2):
		
		pass

def define_logging():

	logging.basicConfig(filename='negation.log',filemode='w',format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

if __name__=="__main__":

	define_logging()
	n = Negation()
	sent1 = u'She is not eating.'.encode('utf-8')
	sent2 = u'She is not going to cinema because I said she is not going.'.encode('utf-8')
	dep1 = n.get_dependencies(sent1,'en')
	logging.info(dep1)
	dep2 = n.get_dependencies(sent2,'en')
	logging.info(dep2)
	n.score_deps(dep1,dep2)
