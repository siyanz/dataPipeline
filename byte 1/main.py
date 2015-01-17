# this is for displaying HTML
from webapp2_extras import jinja2
import cgi
from google.appengine.api import users
import webapp2
import feedparser 
import logging
import urllib
 

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
        feed = feedparser.parse("http://pipes.yahoo.com/pipes/pipe.run?_id=1nWYbWm82xGjQylL00qv4w&_render=rss")

        feed = [{"link": item.link, "title":item.title, "description" : item.description} for item in feed["items"]]

        # this will eventually contain information about the RSS feed
        context = {"feed" : feed, "search": "dog"}

        # here we call render_response instead of self.response.write.
        self.render_response('index.html', **context)

    def post(self):
        logging.info("post")
        terms = self.request.get('search_term')

        terms = urllib.quote(terms)

        # This is the url for the yahoo pipe created in our tutorial
        feed = feedparser.parse("http://pipes.yahoo.com/pipes/pipe.run?_id=1nWYbWm82xGjQylL00qv4w&_render=rss&textinput1=" + terms )
        feed = [{"link": item.link, "title":item.title, "description" : item.description} for item in feed["items"]]

        context = {"feed": feed, "search": terms}
        self.render_response('index.html', **context)

# this sets up the correct callback for [yourname]-byte1.appspot.com
# This is where you would add additional handlers if you 
# wanted to have more subpages on that website.
app = webapp2.WSGIApplication([('/.*', MainHandler)], debug=True)