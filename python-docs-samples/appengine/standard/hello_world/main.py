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
from google.appengine.ext import db
import asknow

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

class MainPage(Handler):
    def get(self):
        items = self.request.get_all('food')
        self.render('shopping_list.html', items = items)
        
class FizzBuzzHandler(Handler):
	def get(self):
		n = self.request.get('n', 0)
		n = n and int(n)
		self.render('fizzbuzz.html', n = n)
		
class Blog(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
		
class BlogHandler(Handler):
	def get(self):
		posts = db.GqlQuery('SELECT * FROM Blog')
		self.render('blog.html', posts = posts)
		
class SinglePostHandler(Handler):
	def get(self, blogid):
		blogkey = int(blogid)
		post = Blog.get_by_id(blogkey)
		if not post:
			self.error(404)
			return
		posts = [ post ]
		self.render('blog.html', posts = posts)
		
class NewPostHandler(Handler):
	def render_form(self, subject="", content="", error=""):
		self.render('newform.html', subject = subject, content = content, error = error)
	
	def get(self):
		self.render_form()
	
	def post(self):
		subject = self.request.get('subject')
		content = self.request.get('content')
		
		if subject and content:
			post = Blog(subject = subject, content = content)
			postid = post.put()
			self.redirect(webapp2.uri_for('blog-post', blogid = postid.id()))
		else:
			self.render_form(subject = subject, content = content, error = 
				'Needs a subject and a title!')
			

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/fizzbuzz', FizzBuzzHandler),
    (r'/blog/?', BlogHandler),
    ('/blog/newpost', NewPostHandler),
    webapp2.Route(r'/blog/<blogid:\d+>', handler = SinglePostHandler, name = 'blog-post'),
], debug=True)
