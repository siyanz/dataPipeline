# standard imports you should have already been using
import webapp2
from webapp2_extras import jinja2
from webapp2_extras import json
import logging
import httplib2
from apiclient.discovery import build
import urllib
import numpy
from django.utils import simplejson

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

    # this will eventually contain information about the RSS feed
    def get(self): 
        """default web page (index.html)""" 


        data = self.get_all_data()
        columns = data['columns']
        logging.info(columns)
        rows = data['rows']

         # specify the ages we will search for
        age_mapping = {u'Infant - Younger than 6 months':'<6mo',
                       u'Youth - Younger than 1 year':'6mo-1yr',
                       u'Older than 1 year':'1yr-6yr',
                       u'Older than 7 years':'>7yr',
                       u'':'Unspecified'}
        # create an 'empty' array storing the number of dogs in each outcome
        
        # specify the outcomes we will search for
        outcomes = ['Adopted', 'Euthanized', 'Foster', 'Returned to Owner', 'Transferred to Rescue Group', 'Other']
        ages = ['<6mo', '6mo-1yr', '1yr-6yr', '>7yr', 'Unspecified']

        age_by_outcome = []
        for age in ages:
            res = {'Age': age}
            for outcome in outcomes:
                res[outcome] = 0
            age_by_outcome = age_by_outcome + [res]

        # find the column id for ages
        ageid = columns.index(u'EstimatedAge')
        
        # find the column id for outcomes
        outcomeid = columns.index(u'OutcomeType')

        # loop through each row
        for row in rows: 
            # get the age of the dog in that row
            age = age_mapping[row[ageid]]
            # get the outcome for the dog in that row
            outcome = row[outcomeid]
            # if the age is a known value (good data) find
            # out which of the items in our list it corresponds to

            if age in ages: age_position = ages.index(age)
            # otherwise we will store the data in the 'Other' age column
            else: age_position = ages.index('Unspecified')

            # if the outcome is a bad value, we call it 'Other' as well
            if outcome not in outcomes: outcome = 'Other'

            # now get the current number of dogs with that outcome and age
            outcomes_for_age = age_by_outcome[age_position]
            # and increase it by one
            outcomes_for_age[outcome] = outcomes_for_age[outcome] + 1
        logging.info(json.encode(age_by_outcome))
        context = {'data':json.encode(age_by_outcome),
                    'y_labels':outcomes,
                    'x_labels':ages}
        # here we call render_response instead of self.response.write.
        self.render_response('index.html', **context)

    def get_all_data(self):
        try:
            fp = open("data/data.json")
            response = simplejson.load(fp)
        except IOError:
            service = build('fusiontables', 'v1', developerKey=API_KEY)
            query = "SELECT * FROM " + TABLE_ID + " WHERE AnimalType = 'DOG'"
            response = service.query().sql(sql=query).execute()
        return response
# this sets up the correct callback for [yourname]-byte1.appspot.com
# This is where you would add additional handlers if you 
# wanted to have more subpages on that website.
app = webapp2.WSGIApplication([('/.*', MainHandler)], debug=True)