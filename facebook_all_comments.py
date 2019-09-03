'''
	This program provides a function that takes the id of a Facebook post in a MongoDB collection
		and expands the list of comments until there is no more paging available.
	Since the FB post may have been collected previously, you need to put in a (possibly new) FB ACCESS_TOKEN
		from the FB graph explorer page.
	The comment field is updated in the mongo collection.

	Make sure the mongod server is running and put the new access token in the variable.

	Command line usage:
        python facebook_all_comments.py <DB name> <collection name> <FB_id> 
    Example:      python facebook_all_comments.py fbusers hillaryclinton 889307941125736_1132603940129467
'''


import json
import re
import sys
import pymongo
import facebook
import requests
from bson.json_util import dumps

ACCESS_TOKEN = 'EAACEdEose0cBAKBdZA6eZAtyiI2Saia0OFM30MZAOh0pTubzdr28ZCmRqGt3H4DU8IvUfg0YaG5jDNTj60g5JXHMEo831NQiPTrlQvpVyMKS4xNS9UIvFLcvkaDi0ZAZCVnXTwVd5y668xq4RyZBWK6x3PVTS4hGMZAbDDy5AC191Of3czPmCpcAjcW4mdDDgkYZD'

# use a main so can get command line arguments
if __name__ == '__main__':
    # Make a list of command line arguments, omitting the [0] element
    # which is the script itself.
    args = sys.argv[1:]
    if not args or len(args) < 3:
        print('usage: python facebook_all_comments.py <DB name> <collection name> <FB_id> ')
        sys.exit(1)
    DBname = args[0]
    DBcollection = args[1]
    FB_id = args[2]
    
    # log in to facebook using the possibly new access token
    fb  = facebook.GraphAPI(ACCESS_TOKEN)
    
    # connect to database server and just let connection errors fail the program
    client = pymongo.MongoClient('localhost', 27017)
    # use the DBname and collection, which will create if not existing
    db = client[DBname]
    collection = db[DBcollection]    
        
    # get the doc with that id
    doc_bson = collection.find_one({'id': FB_id})
    # convert to json
    doc_json_str = dumps(doc_bson)
    doc = json.loads(doc_json_str)

    # get the comments field
    comments = doc['comments']
    # start the process by fetching the next comments (if any) with an updated access token
    if ('next' in comments['paging']):
	    # get the URL for the next page of results using the paging key
	    nextPage = comments['paging']['next']
	    # nextPage is a URL containing a Rest API request;  one of the args is an access_token
	    # make sure the access token is up-to-date by replacing it with the current one
	    # this pattern matches everything up to the access token
	    firstpattern = re.compile('https.+access_token=')
	    firstpart = firstpattern.findall(nextPage)[0]
	    # this pattern matches everything after the access token
	    secondpattern = re.compile('&limit=.+')
	    secondpart = secondpattern.findall(nextPage)[0]
	    # create a new next string with the URL request for more comments
	    nextPage2 = firstpart + ACCESS_TOKEN + secondpart
	    nextResult = requests.get(nextPage2).json()
	    # this result have a list of comments in the data and another paging object for possibly more
	    # create a new list of comments with new paging
	    comments2 = {}
	    comments2['data'] = comments['data'] + nextResult['data']
	    comments2['paging'] = nextResult['paging']
	    # put this new comments list back into the database
	    collection.update({'id': FB_id}, {"$set": {'comments': comments2}}, upsert=False)
	    comments = comments2
	    print('Number comments', len(comments['data']))

	    # check if there are more comments and keep going to get them all, with the same access_token
	    while ('next' in comments['paging']): 
	        # get the URL for the next page of results using the paging key
	        nextPage = comments['paging']['next']
	        # use this URL to get the next comments
	        nextResult = requests.get(nextPage).json()
		    # this result have a list of comments in the data and another paging object for possibly more
		    # create a new list of comments with new paging
	        comments2 = {}
	        comments2['data'] = comments['data'] + nextResult['data']
	        comments2['paging'] = nextResult['paging']
	        # put this new comments list back into the database
	        collection.update({'id': FB_id}, {"$set": {'comments': comments2}}, upsert=False)
	        comments = comments2
	        print('Number comments', len(comments['data']))

    # when done collecting comments
    print('Final comment list has', len(comments['data']), 'comments')

