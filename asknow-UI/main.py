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
from google.appengine.ext import ndb
from google.appengine.api import memcache
import logging
import re
import hashlib, uuid
import json
import datetime
import re

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
	autoescape = True)

class Handler(webapp2.RequestHandler):
	SECRET = 'Secret Udacity secret'
	
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
		
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)
		
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))
		
	def hash_str(self, s):
		return hashlib.sha256(self.SECRET + str(s)).hexdigest()
		
	def verify_hash(self, s, h):
		return self.hash_str(s) == h
		
	def generate_salt(self):
		return uuid.uuid4().hex
		
	def generate_pwhash(self, password, salt):
		return hashlib.sha512(password + salt).hexdigest()
		
	def verify_password(self, pwhash, password, salt):
		return self.generate_pwhash(password, salt) == pwhash
		
	def set_to_json(self):
		self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'

	def print_timestamp(self, timestamp):
		return timestamp.strftime('%a %b %d %H:%M:%S %Y')
		
	def get_username(self):
		cookie = self.request.cookies.get('userid')
		if cookie:
			cookie_split = cookie.split('|')
			if len(cookie_split) == 2:
				useridstr = cookie_split[0]
				userhash = cookie_split[1]
				if self.verify_hash(useridstr, userhash) and useridstr.isdigit():
					user = User.get_by_id(int(useridstr))
					username = user.username
					return username
		return None

class MainPage(Handler):
    def get(self):
        items = self.request.get_all('food')
        self.render('shopping_list.html', items = items)
        
class FizzBuzzHandler(Handler):
	def get(self):
		n = self.request.get('n', 0)
		n = n and int(n)
		self.render('fizzbuzz.html', n = n)
		
class Blog(ndb.Model):
	subject = ndb.StringProperty(required = True)
	content = ndb.TextProperty(required = True)
	created = ndb.DateTimeProperty(auto_now_add = True)
	last_modified = ndb.DateTimeProperty(auto_now = True)
	
class User(ndb.Model):
	username = ndb.StringProperty(required = True)
	password = ndb.StringProperty(required = True)
	salt = ndb.StringProperty(required = True)
	email = ndb.StringProperty()
	
class WikiPage(ndb.Model):
	title = ndb.StringProperty(required = True)
	content = ndb.TextProperty(required = True)
	
class FrontPageJSONHandler(Handler):
	def get(self):
		self.set_to_json()
		posts = ndb.gql('SELECT * FROM Blog')
		postlist = []
		for post in posts:
			cur_post = {}
			cur_post['subject'] = post.subject
			cur_post['content'] = post.content
			if post.created:
				cur_post['created'] = self.print_timestamp(post.created)
			if post.last_modified:
				cur_post['last_modified'] = self.print_timestamp(post.last_modified)
			postlist.append(cur_post)
		self.write(json.dumps(postlist))

class SinglePostJSONHandler(Handler):
	# http://localhost:8080/blog/5629499534213120
	def get(self, blogid):
		self.set_to_json()
		blogkey = int(blogid)
		post = Blog.get_by_id(blogkey)
		if not post:
			self.error(404)
			return
		postjson = {}
		postjson['subject'] = post.subject
		postjson['content'] = post.content
		if post.created:
			postjson['created'] = self.print_timestamp(post.created)
		if post.last_modified:
			postjson['last_modified'] = self.print_timestamp(post.last_modified)
		self.write(json.dumps(postjson))
		
class BlogHandler(Handler):
	def render_blog(self, posts, timediff = -1):
		self.render('blog.html', posts = posts, timediff = timediff)
		
	def get_posts(self, update = False):
		key = 'posts'
		posts = memcache.get(key)
		last_query = memcache.get('last_query')
		if posts is None or update:
			logging.error("DB QUERY")
			posts = ndb.gql('SELECT * FROM Blog')
			last_query = datetime.datetime.now()
			posts = list(posts)
			memcache.set(key, posts)
		memcache.set('last_query', last_query)
		timediff = (datetime.datetime.now()-last_query).seconds
		return posts, timediff
	
	def get(self):
		posts, timediff = self.get_posts()
		self.render_blog(posts, timediff)
		
class SinglePostHandler(BlogHandler):
	def get(self, blogid):
		blogkey = int(blogid)
		key = 'post-%s' % blogkey
		lqkey = 'last_query-%s' % blogkey
		post = memcache.get(key)
		last_query = memcache.get(lqkey)
		if not post:
			post = Blog.get_by_id(blogkey)
			last_query = datetime.datetime.now()
			if not post:
				self.error(404)
				return
			memcache.set(key, post)
			memcache.set(lqkey, last_query)
		posts = [ post ]
		timediff = (datetime.datetime.now()-last_query).seconds
		self.render_blog(posts, timediff)
		
class NewPostHandler(BlogHandler):
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
			self.get_posts(True)
			self.redirect(webapp2.uri_for('blog-post', blogid = postid.id()))
		else:
			self.render_form(subject = subject, content = content, error = 
				'Needs a subject and a title!')
			
class SignUpHandler(Handler):
	def render_form(self, values = {}, errors = {}):
		self.render('signup.html', values = values, errors = errors)
	
	def get(self):
		self.render_form()
	
	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		verify = self.request.get('verify')
		email = self.request.get('email')
		if re.match('^[a-zA-Z0-9_-]{3,20}$', username) and username:
			valid_username = True
		else:
			valid_username = False
		if re.match('^.{3,20}$', password) and password:
			valid_password = True
		else:
			valid_password = False
		if password == verify:
			valid_verify = True
		else:
			valid_verify = False
		if re.match('^[\S]+@[\S]+.[\S]+$', email) or not email:
			valid_email = True
		else:
			valid_email = False
		query = User.query(User.username == username)
		if query.count() > 0:
			user_exists = True
		else:
			user_exists = False
		if valid_username and valid_password and valid_verify and valid_email and not user_exists:
			salt = self.generate_salt()
			pwhash = self.generate_pwhash(password, salt)
			newuser = User(username = username, password = pwhash, salt = salt, email = email)
			newkey = newuser.put()
			newid = newkey.id()
			self.response.headers.add_header('Set-Cookie', 'userid=%s|%s; Path=/' % (newid, self.hash_str(newid)))
			self.redirect('/welcome')
		else:
			values = {}
			values['username'] = username
			values['email'] = email
			errors = {}
			if not valid_username:
				errors['username'] = 'Invalid username'
			elif user_exists:
				errors['username'] = 'This user exists already'
			if not valid_password:
				errors['password'] = 'Invalid password'
			if not valid_verify:
				errors['verify'] = 'Passwords do not match'
			if not valid_email:
				errors['email'] = 'Invalid email'
			self.render_form(values = values, errors = errors)
	
class WelcomeHandler(Handler):	
	def get(self):
		username = self.get_username()
		if username:
			self.render('welcome.html', username = username)
		else:
			self.redirect('/signup')
			
class LoginHandler(Handler):
	def render_form(self, error = ''):
		self.render('login.html', error = error)
	
	def get(self):
		self.render_form()
	
	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		query = User.query(User.username == username)
		user = query.get()
		if username and query.count() > 0:
			pwhash = user.password
			salt = user.salt
			if self.verify_password(pwhash, password, salt):
				userid = user.key.id()
				self.response.headers.add_header('Set-Cookie', 'userid=%s|%s; Path=/' % (userid, self.hash_str(userid)))
				self.redirect('/welcome')
			else:
				self.render_form(error = 'Invalid login')
		else:
			self.render_form(error = 'Invalid login')
			
class LogoutHandler(Handler):
	def get(self):
		self.response.headers.add_header('Set-Cookie', 'userid=; Path=/')
		self.redirect('/signup')
		
class FlushHandler(BlogHandler):
	def get(self):
		memcache.flush_all()
		self.redirect('/blog')
		
class WikiHandler(Handler):
	pagekey = 'wiki-%s'
	def normalize_page_title(self, title):
		if title[-1] == '/':
			return title[:-1]
		else:
			return title
			
	def add(self, title, content):
		newpage = WikiPage(title = title, content = content)
		newpage.put()
		key = self.pagekey % title
		memcache.set(key, content)
	
	def retrieve_page(self, title):
		key = self.pagekey % title
		page = memcache.get(key)
		if not page:
			pass
		return page
		
	def render_page(self, template, title, content, heading = ''):
		if not heading:
			heading = title
		self.render(template, heading = heading, content = content, user = self.get_username(), editlink = webapp2.uri_for('wiki-edit-page', title = title))
		
class WikiEditHandler(WikiHandler):
	def get(self, title):
		username = self.get_username()
		if username:
			title = self.normalize_page_title(title)
			content = self.retrieve_page(title)
			self.render_page('wikieditpage.html', title, content, heading = 'Editing ' + title)
		else:
			self.redirect('/login')
		
	def post(self, title):
		if self.get_username():
			title = self.normalize_page_title(title)
			content = self.request.get('content')
			self.add(title, content)
			self.redirect(webapp2.uri_for(('wiki-page'), title = title))
		else:
			self.redirect('/login')

class WikiPageHandler(WikiHandler):
	
	def get(self, title):
		title = self.normalize_page_title(title)
		content = self.retrieve_page(title)
		username = self.get_username()
		if not content:
			if username:
				self.redirect(webapp2.uri_for('wiki-edit-page', title = title))
			else:
				self.redirect('/login')
		else:
			self.render_page('wikipage.html', title, content)

PAGE_RE = r'/<title:([a-zA-Z0-9_-]+)*/?>'
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/fizzbuzz', FizzBuzzHandler),
    (r'/blog/?', BlogHandler),
    (r'/blog/?.json', FrontPageJSONHandler),
    webapp2.Route(r'/blog/<blogid:\d+>.json', handler = SinglePostJSONHandler, name = 'blog-post-json'),    
    ('/blog/newpost', NewPostHandler),
    webapp2.Route(r'/blog/<blogid:\d+>', handler = SinglePostHandler, name = 'blog-post'),
    ('/signup', SignUpHandler),
    ('/wiki/signup', SignUpHandler),
    ('/welcome', WelcomeHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/blog/flush', FlushHandler),
    webapp2.Route('/wiki/_edit' + PAGE_RE, handler = WikiEditHandler, name = 'wiki-edit-page'),
    webapp2.Route('/wiki' + PAGE_RE, handler = WikiPageHandler, name = 'wiki-page'),
], debug=True)
