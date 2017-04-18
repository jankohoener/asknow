# coding=utf-8
import urllib, urllib2
import json

def link_wikidata_asknow():
	DBPEDIA_API_URL = 'http://dbpedia.org/sparql'
	param = {}
	param['query'] = 'select ?url ?prop where { ?url owl:equivalentProperty ?prop FILTER(regex(?prop, "^http://www.wikidata.org")) }'
	param['default-graph-uri'] = 'http://dbpedia.org'
	param['format'] = 'application/sparql-results+json'
	param['timeout'] = 30000
	params = urllib.urlencode(param)
	url = DBPEDIA_API_URL + '?' + params
	urlobj = urllib2.urlopen(url)
	json_data = json.load(urlobj)
	for prop in json_data['results']['bindings']:
		print '"%s", "%s"' % (prop['url']['value'], prop['prop']['value'])
				
if __name__ == '__main__':
	link_wikidata_asknow()