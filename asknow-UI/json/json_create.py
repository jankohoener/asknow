import json
import urllib

API_URL = 'https://en.wikipedia.org/w/api.php'

for i in xrange(5):
	answer = {}
	title = raw_input('Antwort-Titel\n')
	answer['title'] = title
	req = {}
	req['action'] = 'query'
	req['prop'] = 'info|pageimages|extracts'
	req['titles'] = title
	req['inprop'] = 'url'
	req['piprop'] = 'original'
	req['exintro'] = True
	req['exsectionformat'] = 'raw'
	req['format'] = 'json'
	req['indexpageids'] = True
	params = urllib.urlencode(req)
	url = API_URL + '?' + params
	urlobj = urllib.urlopen(url)
	json_data = json.load(urlobj)
	pageid = json_data['query']['pageids'][0]
	answer['abstract'] = json_data['query']['pages'][pageid]['extract']
	answer['wplink'] = json_data['query']['pages'][pageid]['fullurl']
	answer['imgsrc'] = json_data['query']['pages'][pageid]['thumbnail']['original']
	with open('answer-0%d.json' % i, 'w') as f:
		f.write(json.dumps(answer))
		