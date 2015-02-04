# standard imports you should have already been using
import webapp2
import logging
from webapp2_extras import jinja2
import urllib

# this library is for decoding json responses
from webapp2_extras import json

# this is used for constructing URLs to google's APIS
from apiclient.discovery import build

API_KEY = 'AIzaSyDOI185_gTElbbCD1BUgalIiDZ4XeRlXO8'
TABLE_ID = '1V-zsxH7mLEiM6ueBDTLbL3PcPbN_V_HG6W3nA_54'
# This uses discovery to create an object that can talk to the 
# fusion tables API using the developer key
service = build('fusiontables', 'v1', developerKey=API_KEY)

# BaseHandler subclasses RequestHandler so that we can use jinja
class BaseHandler(webapp2.RequestHandler):

    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app)

        # This will call self.response.write using the specified template and context.
        # The first argument should be a string naming the template file to be used. 
        # The second argument should be a pointer to an array of context variables
        #  that can be used for substitutions within the template
    def render_response(self, _template, **context):
        # Renders a template and writes the result to the response.
        rv = self.jinja2.render_template(_template, **context)
        self.response.write(rv)

        # Class MainHandler now subclasses BaseHandler instead of webapp2
class MainHandler(BaseHandler):
    
         # This method should return the html to be displayed
    def get(self):

        # this will eventually contain information about the RSS feed
        context = {}
        self.get_all_data()
        # here we call render_response instead of self.response.write.
        self.render_response('index.html', **context)

    def get_all_data(self):
        query = "SELECT * FROM " + TABLE_ID + " WHERE  AnimalType = 'DOG' LIMIT 2"
        response = service.query().sql(sql=query).execute()
        logging.info(response['columns'])
        logging.info(response['rows'])

        return response
# this sets up the correct callback for [yourname]-byte1.appspot.com
# This is where you would add additional handlers if you 
# wanted to have more subpages on that website.
app = webapp2.WSGIApplication([('/.*', MainHandler)], debug=True)