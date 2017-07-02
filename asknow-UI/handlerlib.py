# -*- coding: utf-8 -*-
import webapp2
import os
import jinja2
import hashlib, uuid

ASKNOW_PATH = '/asknow/'

def joinfunc(array, wrapper):
	wrap_array = [wrapper % x for x in array]
	a = []
	if ', '.join(wrap_array[0:-1]):
		a.append(', '.join(wrap_array[0:-1]))
	if wrap_array[-1]:
		a.append(wrap_array[-1])
	return ' and '.join(a)

def answerclass(answers):
	if answers.get('answered'):
		return 'answered'
	elif answers.get('leninfo') > 0:
		return 'not-answered-entities'
	else:
		return 'not-answered'

class Handler(webapp2.RequestHandler):
	template_dir = os.path.join(os.path.dirname(__file__), 'templates')
	
	jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
	autoescape = True)
	jinja_env.filters['joinfunc'] = joinfunc
	jinja_env.filters['answerclass'] = answerclass
	
	SECRET = "The AskNow secret"
	
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
		
	def render_str(self, template, **params):
		t = self.jinja_env.get_template(template)
		return t.render(params)
		
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))
		
	def hash_str(self, s):
		return hashlib.sha256(self.SECRET + str(s)).hexdigest()
		
	def reset_cookie(self, cookie):
		self.response.headers.add_header('Set-Cookie', '%s=; Path=/' % cookie)
		
	def generate_salt(self):
		return uuid.uuid4().hex
		
	def generate_pwhash(self, password, salt):
		return hashlib.sha512(password + salt).hexdigest()
		
	def verify_password(self, pwhash, password, salt):
		return self.generate_pwhash(password, salt) == pwhash
		
	def retrieve_title_from_url(self, url):
		return url.replace('http://dbpedia.org/resource/', '').replace('_', ' ')
	
	def encode_title(self, title):
		return title.replace(' ', '_')