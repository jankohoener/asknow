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

from google.appengine.ext import ndb

class AskNowUser(ndb.Model):
	username = ndb.StringProperty(required = True)
	password = ndb.StringProperty(required = True)
	salt = ndb.StringProperty(required = True)
	email = ndb.StringProperty()
	created = ndb.DateTimeProperty(auto_now_add=True)
	
class AskNowQuestion(ndb.Model):
	userid = ndb.KeyProperty(AskNowUser, required=True)
	question = ndb.StringProperty(required=True)
	asked = ndb.DateTimeProperty(auto_now_add=True)