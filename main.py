#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
#
import os
from google.appengine.ext.webapp import template

import cgi

import urllib

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

"""Model for the Feature object"""
class Feature(db.Model):
    author = db.UserProperty()
    name = db.StringProperty(multiline=False)
    description = db.TextProperty()
    votes = db.IntegerProperty()
    done = db.BooleanProperty(default=False)

class MainPage(webapp.RequestHandler):
    def get(self):
        features_query = Feature.all().order('-votes').order('name')
        features = features_query.fetch(999999)

	""" get the selected item """
	feature_name = self.request.get('feature_name')
	if len(feature_name) > 0:
		pets = db.GqlQuery("SELECT * FROM Feature WHERE name = :1", feature_name)
		selected_feature = pets.get()
	else:
		selected_feature = None

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'features': features,
            'url': url,
            'url_linktext': url_linktext,
	    'selected_feature': selected_feature,
            }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

""" 
Create new Feature item 
   Replaces by name
"""
class AddFeature(webapp.RequestHandler):
    def post(self):

	pets = db.GqlQuery("SELECT * FROM Feature WHERE name = :1", self.request.get('old_name'))
	old_feature = pets.get()

        feature = Feature()

        if users.get_current_user():
            feature.author = users.get_current_user()

        feature.name = self.request.get('name')
        feature.description = self.request.get('description')
        feature.votes = 0
	feature.done = False

	if old_feature != None:
		feature.votes = old_feature.votes
		feature.done = old_feature.done
		old_feature.delete()


        feature.put()
        self.redirect('/')

class AddVote(webapp.RequestHandler):
     def post(self):
	pets = db.GqlQuery("SELECT * FROM Feature WHERE name = :1", self.request.get("name"))
	feature = pets.get();
	feature.votes += 1;
	feature.put();
	self.redirect('/');

class RemoveVote(webapp.RequestHandler):
     def post(self):
	pets = db.GqlQuery("SELECT * FROM Feature WHERE name = :1", self.request.get("name"))
	feature = pets.get();
	feature.votes -= 1;
	feature.put();
	self.redirect('/');

class Done(webapp.RequestHandler):
     def post(self):
	pets = db.GqlQuery("SELECT * FROM Feature WHERE name = :1", self.request.get("name"))
	feature = pets.get();
	feature.done = not feature.done;
	feature.put();
	self.redirect('/');

class Select(webapp.RequestHandler):
     def post(self):
	pets = db.GqlQuery("SELECT * FROM Feature WHERE name = :1", self.request.get("name"))
	feature = pets.get();
	feature.name = feature.name;
	feature.put();
    	self.redirect('/?' + urllib.urlencode({'feature_name': feature.name}))

class Delete(webapp.RequestHandler):
     def post(self):
	pets = db.GqlQuery("SELECT * FROM Feature WHERE name = :1", self.request.get("name"))
	feature = pets.get();
	feature.delete();
	self.redirect('/');	

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/sign', AddFeature), ('/vote', AddVote), ('/removeVote', RemoveVote), ('/done', Done), ('/select', Select), ('/delete', Delete)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()