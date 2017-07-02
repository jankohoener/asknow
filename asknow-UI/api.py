# -*- coding: utf-8 -*-
# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import json
from google.appengine.api import memcache, urlfetch, urlfetch_errors
import logging
from handlerlib import *
from datatypes import *
from userauth import *
import urllib, urllib2
from urllib2 import Request
import os
from google.appengine.api.urlfetch_errors import *


class AskNowJSONAnswerHandler(Handler):
	GENESIS_API_URL = 'http://genesis.aksw.org/api/'
	GENESIS_APIS = ['description', 'similar', 'related', 'images', 'videos']
	GENESIS_QUERY_APIS = ['images', 'videos']
	GENESIS_API_JSON_MAPPING = {'related': 'relatedEntities', 'similar': 'similarEntities'}
	DBPEDIASL_URL = 'http://model.dbpedia-spotlight.org/en/annotate'
	DBPEDIA_URL = 'http://dbpedia.org/resource/'
	DBPEDIA_API_URL = 'http://dbpedia.org/sparql'
	DBPEDIASL_CONF = 0.4

	def retrieve_info(self, titles):
		resp = {}
		resp['information'] = []
		resp['answers'] = []
		for title in titles:
			title_type = type(title)
			if title_type is int or title_type is float:
				resp['answers'].append("{:,}".format(title))
				titles.remove(title)
				continue
			elif title_type is bool:
				resp['answers'].append(('Yes', 'No')[title])
				titles.remove(title)
				continue
			elif title_type is not str:
				raise ValueError('title must be string, int, float or boolean')
			# elif title_type is str:
			cur_info = {}
			cur_info['title'] = title
			for api in self.GENESIS_APIS:
				dbpurl = {}
				if api in self.GENESIS_QUERY_APIS:
					dbpurl['q'] = title
				else:
					dbpurl['url'] = self.DBPEDIA_URL + self.encode_title(title)
				dbpjson = json.dumps(dbpurl)
				url = self.GENESIS_API_URL + api
				retry = 2
				while retry:
					try:
						urlobj = urlfetch.fetch(url, method='POST', payload=dbpjson, headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Connection': 'keep-alive'}, deadline=1)
					except:
						retry = retry - 1
						if not retry:
							if api in self.GENESIS_API_JSON_MAPPING:
								cur_info[self.GENESIS_API_JSON_MAPPING[api]] = None
							else:
								cur_info[api] = None
							break
					else:
						if urlobj.status_code == 200:
							cur_info.update(json.loads(urlobj.content))
							break
						else:
							retry = retry - 1
							if not retry:
								if api in self.GENESIS_API_JSON_MAPPING:
									answer[self.GENESIS_API_JSON_MAPPING[api]] = None
								else:
									answer[api] = None
								break
			resp['information'].append(cur_info)
		resp['answers'].extend(titles)
		resp['lenanswers'] = len(resp['answers'])
		resp['status'] = 0
		resp['message'] = 'Connection successful.'
				
			
		"""
		for title in titles:
			self.retrieve_summary(title)
			self.retrieve_description(title)
			self.retrieve_similar(title)
			self.retrieve_images(title)
			self.retrieve_videos(title)
			
			answers: [ {objects} ]
			objects: { "summary":
					   "description":
					   "similar":
					   "images":
					   "videos":
					   }
		
		if len(titles) == 0:
			answers['lentitles'] = len(answers['titles'])
			return answers
		req['action'] = 'query'
		req['prop'] = 'info|pageimages|extracts'
		req['titles'] = '|'.join(titles)
		req['inprop'] = 'url'
		req['piprop'] = 'thumbnail'
		req['pilicense'] = 'free'
		req['pithumbsize'] = 300
		req['exintro'] = True
		req['exsectionformat'] = 'raw'
		req['format'] = 'json'
		req['indexpageids'] = True
		req['redirects'] = True
		while True:
			try:
				params = urllib.urlencode(req)
				url = self.API_URL + '?' + params
				urlobj = urlfetch.fetch(url)
			except:
				answer['error'] = 2
				answer['message'] = 'Cannot connect to Wikipedia API'
				return answer
			else:
				json_data = json.loads(urlobj.content)
				if json_data.get('error'):
					answer['error'] = 3
					answer['message'] = 'Error parsing Wikipedia API: %s' % json_data['error']['info']
					answers['information'].append(answer)
					continue
				pageids = json_data['query']['pageids']
				for pageid, info in json_data['query']['pages'].items():
					if info.get('missing') == '': # error case: page doesn't exist. Get out!
						if info.get('title'):
							if info['title'] not in answers['titles']:
								answers['titles'].append(info['title'])
						continue
					if not answer.get(pageid):
						answer[pageid] = {}
					if info.get('title'):
						if info['title'] not in answers['titles']:
							answers['titles'].append(info['title'])
					if info.get('missing') == '':
						continue
					answer[pageid]['title'] = info['title']
					answer[pageid]['relents'] = self.retrieve_related_entities(info['title'])
					answer[pageid]['lenrelent'] = len(answer[pageid]['relents'])
					if info.get('extract'):
						answer[pageid]['abstract'] = info['extract']
					if info.get('fullurl'):
						answer[pageid]['wplink'] = info['fullurl']
					if info.get('thumbnail'):
						answer[pageid]['imgsrc'] = info['thumbnail']['source']
					if json_data.get('continue'):
						req.update(json_data['continue'])
				if json_data.get('batchcomplete') == '':
					break
		answers['information'] = answer.values()
		answers['lentitles'] = len(answers['titles'])
		return answers
		"""
		return resp
		
	def retrieve_entities(self, phrase):
		param = {}
		param['text'] = phrase
		param['confidence'] = self.DBPEDIASL_CONF
		params = 'text=%s&confidence=%s' % (param['text'], param['confidence'])
		url = self.DBPEDIASL_URL + '?' + urllib.urlencode(param)
		headers = { 'Accept' : 'application/json' }
		logging.debug(url)
		retry = 2
		while retry:
			try:
				a = urlfetch.fetch(url, headers = headers)
			except:
				retry = retry - 1
				if not retry:
					return []
			else:
				if a.status_code == 200:
					entityobj = json.loads(a.content)
					logging.debug(entityobj)
					if entityobj.get('Resources'):
						titles = []
						for entity in entityobj['Resources']:
							if entity.get('@URI'):
								title = self.retrieve_title_from_url(entity['@URI']).encode('utf-8')
								titles.append(title)
						if titles:
							return titles
						else:
							return []
					else:
						return []
				else:
					return []

	"""def retrieve_related_entities(self, title):
		param = {}
		param['query'] = 
		PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX dbo:<http://dbpedia.org/ontology/>
		PREFIX dbr:<http://dbpedia.org/resource/>
		PREFIX vrank:<http://purl.org/voc/vrank#>
		SELECT DISTINCT ?url FROM <http://people.aifb.kit.edu/ath/#DBpedia_PageRank> WHERE {
		<http://dbpedia.org/resource/%s> ?p ?url. ?url vrank:hasRank/vrank:rankValue ?w.
		FILTER( regex(str(?url), '^(?!http://dbpedia.org/resource/Category).+'))
		FILTER( regex(str(?url), '^(?!http://dbpedia.org/class/yago/).+'))
		FILTER( regex(str(?url), '^(?!http://www.wikidata.org/entity).+'))}
		ORDER BY DESC(?w) LIMIT 20 % self.encode_title(title)
		param['default-graph-uri'] = 'http://dbpedia.org'
		param['format'] = 'application/sparql-results+json'
		param['timeout'] = 30000
		relents = []
		params = urllib.urlencode(param)
		url = self.DBPEDIA_API_URL + '?' + params
		urlobj = urllib2.urlopen(url)
		json_data = json.load(urlobj)
		for prop in json_data['results']['bindings']:
			relent = {}
			relent['url'] = prop['url']['value']
			relent['title'] = self.retrieve_title_from_url(relent['url'])
			relents.append(relent)
		return relents
		"""
	
	def retrieve_titles(self, question):
		# FIXME: this should use a call to an AskNow API!!!
		#if type(question) is not str or not question:
		#	raise ValueError('Question must be a non-null string')
		known_answers = {
			'how many symphonies did beethoven compose': [9],
			'how many inhabitants does oberhausen have': [210934],
			'is albert einstein alive': [True],
			'is kanye west alive': [False],
			'who is the president of the united states': ['Barack Obama'],
			'how many goals did gerd müller score': ['Gerd Müller'],
			'who is the president elect of the united states': ['Donald Trump'],
			'in which city was beethoven born': ['Bonn'],
			'in which city was adenauer born': ['Cologne'],
			'what country is shah rukh khan from': ['India'],
			'what are the capitals of germany and india': ['Berlin', 'New Delhi'],
			'what are the capitals of germany, india and usa': ['Berlin', 'New Delhi', 'Washington D.C.'],
			'what are the capitals of germany, india, usa and france': ['Berlin', 'New Delhi', 'Washington D.C.', 'Paris']
		}
		if question in known_answers:
			return known_answers[question]
		else:
			return []

	def get(self):
		query = question = self.request.get('q')
		question = question.lower().replace('?', '')
		question = question.encode('utf-8')
		answers = {}
		if query:
			titles = self.retrieve_titles(question)
			logging.debug(titles)
			if len(titles) > 0:
				answers = self.retrieve_info(titles)
				if answers.get('error'):
					answers['answered'] = False
				else:
					answers['answered'] = True
				if len(answers['information']) == 0 and answers.get('lenanswers') > 0:
					entitytitles = self.retrieve_entities(question)
					entityanswers = self.retrieve_info(entitytitles)
					answers['information'].extend(entityanswers['information'])
			else:
				titles = self.retrieve_entities(question)
				answers = self.retrieve_info(titles)
				answers['answers'] = []
				answers['lenanswers'] = 0
		else:
			answers = { 'status': 2, 'message': 'Application needs a q parameter, none given.' }
		answers['question'] = query
		json_string = json.dumps(answers)
		self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
		self.write(json_string)