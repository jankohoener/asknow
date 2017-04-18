# coding=utf-8
import urllib, urllib2
import json

def fetch_wikidata_props():
	WIKIDATA_API_URL = 'https://www.wikidata.org/w/api.php'
	param = {}
	param['action'] = 'query'
	param['format'] = 'json'
	param['generator'] = 'allpages'
	param['gapnamespace'] = 120
	param['gaplimit'] = 'max'
	param['prop'] = 'pageterms'
	param['wbptterms'] = 'label|alias'
	while True:
		params = urllib.urlencode(param)
		url = WIKIDATA_API_URL + '?' + params
		urlobj = urllib2.urlopen(url)
		json_data = json.load(urlobj)
		for pageid, resp in json_data['query']['pages'].items():
			labels = list(resp['terms']['label'])
			if resp['terms'].get('alias'):
				labels.extend(resp['terms']['alias'])
			filename = resp['title'].replace('Property:', '')
			filestream = open(filename, 'w')
			content = '\n'.join(labels)
			filestream.write(content.encode('utf-8'))
			filestream.close()
		if json_data.get('continue'):
			param.update(json_data['continue'])
		else:
			break
				
if __name__ == '__main__':
	fetch_wikidata_props()