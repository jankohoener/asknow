# -*- coding: utf-8 -*-
# Copyright 2017 Janko Hoener
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
from handlerlib import Handler
from datatypes import AskNowUser
import re


class AskNowLogoutHandler(Handler):
	def get(self):
		self.reset_cookie('userid')
		self.redirect(webapp2.uri_for('demo'))
		
class AskNowSignUpHandler(Handler):
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
		query = AskNowUser.query(AskNowUser.username == username)
		if query.count() > 0:
			user_exists = True
		else:
			user_exists = False
		if valid_username and valid_password and valid_verify and valid_email and not user_exists:
			salt = self.generate_salt()
			pwhash = self.generate_pwhash(password, salt)
			newuser = AskNowUser(username = username, password = pwhash, salt = salt, email = email)
			newkey = newuser.put()
			newid = newkey.id()
			self.response.headers.add_header('Set-Cookie', 'userid=%s|%s; Path=/' % (newid, self.hash_str(newid)))
			self.redirect(webapp2.uri_for('demo'))
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

class AskNowLoginHandler(Handler):
	def render_form(self, error = ''):
		self.render('login.html', error = error)
	
	def get(self):
		self.render_form()
	
	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		query = AskNowUser.query(AskNowUser.username == username)
		user = query.get()
		if username and query.count() > 0:
			pwhash = user.password
			salt = user.salt
			if self.verify_password(pwhash, password, salt):
				userid = user.key.id()
				self.response.headers.add_header('Set-Cookie', 'userid=%s|%s; Path=/' % (userid, self.hash_str(userid)))
				self.redirect(webapp2.uri_for('demo'))
			else:
				self.render_form(error = 'Invalid login')
		else:
			self.render_form(error = 'Invalid login')