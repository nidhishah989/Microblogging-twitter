###########################################################################################
## CLASS : CPSC-449-section-1
## ASSIGNMENT: Microblogging service-twitter
## STUDENTS INFORMATION FROM Group ::
    # Nidhi Shah- 
    # Priyanka Kadam 
    # Robert Nguyen 
###########################################################################################

"""Functions this timeline service provide..
   1. internal function: for user authentication- request user service
   2. Public Timeline: show all posts done by all
   3. User Timeline: show all posts that user have created( with authentication)
   4. Home Timeline: show all posts that freinds whom user follow have created (user authentication)
   5. create post: create a new post by user (user authentication)
   6. Repost: create a repost (user authentication)
   7. healthcheck function will support healthcheck for serviceregistry
   8. New: endpoint:asynpost
   """
########### importing require modules #################################
import configparser
import logging.config
from falcon import response
import falcon
import hug
import sqlite_utils
import requests
import os
import greenstalk
import json
#####################################################################
client = greenstalk.Client(('127.0.0.1', 11300))
#####################################################################
#Load configuration
config = configparser.ConfigParser()
config.read("./etc/api.ini")
logging.config.fileConfig(config["logging"]["config"], disable_existing_loggers=False)

#####################################################################
##A Directive for Sqlite database - for post.db --(tables: post and repost)
@hug.directive()
def sqlite_timeline(section="sqlite_timeline", key="dbfile", **kwargs):
    dbfile = config[section][key]
    return sqlite_utils.Database(dbfile)

# Directive for log events
hug.directive()
def log(name=__name__, **kwargs):
    return logging.getLogger(name)

#startup function- to register itself in service registry
@hug.startup()
def startup(api):
    url= config["service_registry_url"]["url_info"]
    pollsport= os.environ.get("PORT")
    request_url=url
    result = requests.post(request_url,data={"servicename":"timeline","healthurl":"/health-check/","serviceport":pollsport})

####################################################################
# the inside function will help the timelines for usre authentication
# by requesting the user service.
@hug.cli()
def auth(username,password,status=hug.falcon.HTTP_200):
    
    # get url for serviceregistry from config file, to get userservice port number
    url=config["service_registry_url"]["service_check"]
    # request service registry for user service port number, if the userservice is registered
    result = requests.get(f'{url}userprofile')

    # if the user service is registered, the service registry have sent 200 status.
    if result.status_code==200:
        # get the userprofile port info
        portinfo=result.json()
        port=portinfo['portnumber']
        # now do the userprofile request for authentication
        authRequest=requests.get(f'http://localhost:{port}/authentication/{username}')
        authuser= authRequest.json()
        #check password is incorrect .. user is unauthorized
        if authuser["password"] != password:
            response.status=hug.falcon.HTTP_401
        else:
            # all good, user is fully authorized
            return status
    # if the user service is not registered, the service registry have sent 409 status.
    else:
        # this should send the 502 gateway
        #response.status=hug.falcon.HTTP_502
        #status=hug.falcon.HTTP_502
        raise falcon.HTTPBadGateway
####################################################################
#Routes
###############################################################################
# healthcheck routes
@hug.get("/health-check/",status=hug.falcon.HTTP_200)
def healthchecklikeservice(response):
    print(" timeline is available")
####################################################################
#show all posts in reverse chronological order(public timeline)
# no user authentication need
@hug.get("/publictimeline/")
def public_timeline(db: sqlite_timeline):

    return {"Posts": db["post"].rows_where(order_by="PostID desc")}

######################################################################
# for authentication of user- will call inside function with hug basic authentication
basic_authentication = hug.authentication.basic(auth)

#####################################################################
#show particular user's timeline / posts only / in reverse chronological order( user timeline)
# user authentication is require before execution of this function
@hug.get("/usertimeline/{username}",requires=basic_authentication)
def user_timeline(response,user:hug.directives.user,username: hug.types.text, db: sqlite_timeline):

    posts = []
    values = []
    values.append(username)
    try:
        # get all post that user have created. with reverse chronological order
        posts=db["post"].rows_where("AuthorName=?",values,order_by="PostID desc")
    except sqlite_utils.db.NotFoundError:
        response.status = hug.falcon.HTTP_404
    return {"Posts": posts}
##################################################################################
#show user's home timeline, showing only posts by the people the user follows (home timeline)
# user authentication is require before execution of this function
@hug.post("/hometimeline/",requires=basic_authentication)
def home_timeline(request,response,user:hug.directives.user,username:hug.types.text,friends:hug.types.json,db:sqlite_timeline):

    values=[]
    posts=[]
    fragement="AuthorName=? "
    fragement2="OR AuthorName=?"
    try:
        #check the response of the userservice-following-
        # if that service thrown a error and can't find following
        # this can not go further. so throw same error
        for i in friends:
            if i == "error":
                raise Exception (f'{friends[i]}')
            else:
                values.append(friends[i])
    except Exception as err:
        response.status = hug.falcon.HTTP_409
        return {"error": str(err)}

    # after getting a list of friends that use follow,
    # prepare for the database query and do the query to get posts done by user's freinds
    try:

        for i in range(len(values)-1):
            fragement = fragement + fragement2
        # database query---
        posts=db["post"].rows_where(fragement,values,order_by="PostID desc")
    except sqlite_utils.db.NotFoundError:
        response.status = hug.falcon.HTTP_404

    return {"Posts": posts}


#####################################################################################
#posts# user is creating a new post..
# user authentication is require before execution of this function
@hug.post("/createpost/",status=hug.falcon.HTTP_201, requires=basic_authentication)
def create_post(response,user:hug.directives.user,username:hug.types.text,post:hug.types.text, posttimestamp:hug.types.text,db: sqlite_timeline):

    posts=db["post"]
    try:
        # gather all information that need to insert in the database table -post
        postdata={"Post":post,"PostTimestamp":posttimestamp,"AuthorName":username}
        posts.insert(postdata)
        postdata["PostID"]=posts.last_pk
        return postdata
    except Exception as e:
        response.status = hug.falcon.HTTP_409
        return {"error": str(e)}

########################################################################
#Reposts - user is creating a repost..
# user authentication is require before execution of this function
# this functon will recieve the actualpostid from the frontend service,
# with require repost data
# the actual post id is our URL for the repost service
@hug.post("/repost/",status=hug.falcon.HTTP_201, requires=basic_authentication)
def re_post(response,user:hug.directives.user,username:hug.types.text,actualpostid:hug.types.number,repost:hug.types.text, posttimestamp:hug.types.text,db: sqlite_timeline):
   
    reposts=db["repost"]
    try:

        repostdata={"username":username,"repost":repost,"actualpostid":actualpostid,"reposttimestamp":posttimestamp}
        reposts.insert(repostdata)
        repostdata["repostid"]=reposts.last_pk
        return repostdata
    except Exception as e:
        response.status = hug.falcon.HTTP_409
        return {"error": str(e)}
##############################################################################
# Asynchronize post the tweet
@hug.post("/addpostasync/", status =hug.falcon.HTTP_202,requires=basic_authentication)
def addnewpostasync(response,username:hug.types.text,post:hug.types.text, posttimestamp:hug.types.text):
    try:
        #creating body for pollworker
        body1=json.dumps({
            'text':post,
            'author':username,
        })
        # create tube for pollworker to check the post have the url of poll and if so do validation for pollid
        client.use("pollasyncwork")
        client.put(body1)

        # creating body for postworker
        body = json.dumps({
        'username': username,
        'postdata': post,
        'timeline': posttimestamp,
        })

        # create tube for postworker to check the jobs related to post
        client.use("postasyncwork")
        client.put(body)
      
        return response.status

    except Exception as e:
        response.status = hug.falcon.HTTP_409
        return {"error": str(e)}
    
