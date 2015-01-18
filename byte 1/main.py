# this is for displaying HTML
from webapp2_extras import jinja2
import cgi
from google.appengine.api import users
import webapp2
import feedparser 
import logging
import urllib
import datetime
 

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
        feed = feedparser.parse("https://pipes.yahoo.com/pipes/pipe.run?_id=a3f7d6f6a403e7ccec84c895972bb154&_render=rss")

        feed = [{"link": item.link, "title":item.title, "description" : item.description} for item in feed["items"]]

        # this will eventually contain information about the RSS feed
        context = {"feed" : feed}

        # here we call render_response instead of self.response.write.
        self.render_response('index.html', **context)

    def post(self):
        logging.info("post")
        terms = self.request.get("source")

        if terms == "1":
            terms = "https://pipes.yahoo.com/pipes/pipe.run?_id=a3f7d6f6a403e7ccec84c895972bb154&_render=rss"
            selected = "CNN"
        elif terms == "2":
            terms = "http://rss.nytimes.com/services/xml/rss/nyt/World.xml"
            selected = "New York Times"
        elif terms == "3":
            terms = "http://mf.feeds.reuters.com/reuters/UKWorldNews"
            selected = "Reuter"
        elif terms == "4":
            terms = "https://pipes.yahoo.com/pipes/pipe.run?_id=f3650894a77fa1323e83eebe8beace62&_render=rss"
            selected = "BBC"
        # This is the url for the yahoo pipe created in our tutorial
        feed = feedparser.parse(terms)
        feed = [{"link": item.link, "title":item.title, "description" : item.description, "pubDate": item.published} for item in feed["items"]]

        all_time = []
        total_time = 0
        news_count=20

        for item in feed:
            date = item["pubDate"].split(" ")[4]
            time = datetime.time(hour=int(date[0:2]), minute=int(date[3:5]), second=int(date[6:8]))
            all_time.append(time)

        for n in range(1, news_count):
            lapse = datetime.timedelta(
                    hours = (all_time[n-1].hour - all_time[n].hour),
                    minutes = (all_time[n-1].minute - all_time[n].minute)
                    )
            total_time += lapse.seconds

        avg = total_time/(news_count-1)

        hour=int(avg/60/60)
        minute=int((avg-hour*60*60)/60)
        second=avg-hour*60*60-minute*60

        context = {"feed": feed, "h": hour, "m": minute, "s": second, 
            "last": all_time[0], "time_zone": feed[0]["pubDate"].split(" ")[-1], 
            "date":feed[0]["pubDate"].split(" ")[0], "selected": selected}
        self.render_response('index.html', **context)

# this sets up the correct callback for [yourname]-byte1.appspot.com
# This is where you would add additional handlers if you 
# wanted to have more subpages on that website.
app = webapp2.WSGIApplication([('/.*', MainHandler)], debug=True)