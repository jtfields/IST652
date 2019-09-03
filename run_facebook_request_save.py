'''
    This main function uses a facebook request function to get a connection field for a facebook user,
        for example, the field 'feed' will retrieve all the posts (with comments and likes)
    It assumes that it will save retrieved tweets to a Mongo DB collection
        make sure that mongod is running the mongo server before running this program
    Command line usage:
        python run_facebook_request_save.py <query> <field> <num> <DB name> <collection name>
    Example:      python run_facebook_request_save.py Delta feed 400 FBusers delta

'''

import sys
import json
import facebook
from facebook_request_fn import facebook_connection_request
from facebook_login_fn import fb_login
from DB_fn import save_to_DB

# simple utility function, pretty print, to nicely print dictionary of json objects
def pp(o):
    print (json.dumps(o, indent=1))

# test program for facebook multiple request function 
if __name__ == '__main__':
    # Make a list of command line arguments, omitting the [0] element
    # which is the script itself.
    args = sys.argv[1:]
    if not args or len(args) < 5:
        print('usage: python run_facebook_request_save.py <query> <field> <num> <DB name> <collection name>')
        sys.exit(1)
    query = args[0]
    field = args[1]
    num = int(args[2])
    DBname = args[3]
    DBcollection = args[4]
    
    # make sure that this has a current access token
    fb  = fb_login()

    # set the limit to the number of items to get per request
    kw = { }
    kw['limit'] = 100
    # other keywords that can be used here include 'after', 'since' and 'after_id'
    #   in order to collect a full set of items
    # examples of since and until format:  
    #       kw['since'] = 2011-07-01
    #       kw['until'] = '2014-03-04'
    
    # call the function with the query and the field
    results = facebook_connection_request(fb, query, field, num)
    
    # save the results to a database collection
    # use the save and load functions in this program
    save_to_DB(DBname, DBcollection, results)

    print ('number saved', len(results))
    
    # in the case of results from the request for 'feed', results have "from"->"name" and "updated_time" fields
    print('First 20 posts:')
    for post in results[:20]:
        # optional message field
        if 'message' in post.keys():
            pnum = min([len(post["message"]), 100])
            print ("Post from:", post['name'], " Date: ", post["updated_time"], " Message begin: ", post["message"][:pnum])
        else:
            print ("Post from:", post['name'], " Date: ", post["updated_time"])
            
