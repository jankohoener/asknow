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