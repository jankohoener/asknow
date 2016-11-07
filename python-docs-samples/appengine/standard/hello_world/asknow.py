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

import webapp2
import jinja2
import os

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
	autoescape = True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
		
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)
		
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))
		
class AskNowDemoHandler(Handler):
	# https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&titles=Barack+Obama&exsentences=5
	def get(self):
		if self.request.get('q'):
			answer = {}
			answer['title'] = 'Barack Obama'
			answer['abstract'] = "<p><b>Barack Hussein Obama II</b> (<span><small>US</small> <span>/<span><span title=\"'b' in 'buy'\">b</span><span title=\"/\u0259/ 'a' in 'about'\">\u0259</span><span title=\"/\u02c8/ primary stress follows\">\u02c8</span><span title=\"'r' in 'rye'\">r</span><span title=\"/\u0251\u02d0/ 'a' in 'father'\">\u0251\u02d0</span><span title=\"'k' in 'kind'\">k</span></span> <span><span title=\"'h' in 'hi'\">h</span><span title=\"/u\u02d0/ long 'oo' in 'food'\">u\u02d0</span><span title=\"/\u02c8/ primary stress follows\">\u02c8</span><span title=\"'s' in 'sigh'\">s</span><span title=\"/e\u026a/ long 'a' in 'base'\">e\u026a</span><span title=\"'n' in 'no'\">n</span></span> <span><span title=\"/o\u028a/ long 'o' in 'code'\">o\u028a</span><span title=\"/\u02c8/ primary stress follows\">\u02c8</span><span title=\"'b' in 'buy'\">b</span><span title=\"/\u0251\u02d0/ 'a' in 'father'\">\u0251\u02d0</span><span title=\"'m' in 'my'\">m</span><span title=\"/\u0259/ 'a' in 'about'\">\u0259</span></span>/</span></span>; born August 4, 1961) is an American politician who is the 44th and current President of the United States. He is the first African American to hold the office and the first president born outside the continental United States. Born in Honolulu, Hawaii, Obama is a graduate of Columbia University and Harvard Law School, where he was president of the <i>Harvard Law Review</i>. He was a community organizer in Chicago before earning his law degree. He worked as a civil rights attorney and taught constitutional law at the University of Chicago Law School between 1992 and 2004.</p>"
			answer['wplink'] = 'https://en.wikipedia.org/wiki/Barack_Obama'
			answer['imgsrc'] = 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/President_Barack_Obama.jpg/220px-President_Barack_Obama.jpg'
			self.render('asknowdemo_answer.html', answer = answer, q = self.request.get('q'))
		else:
			self.render('asknowdemo.html')
		

app = webapp2.WSGIApplication([
    ('/asknow-demo', AskNowDemoHandler),
], debug=True)
