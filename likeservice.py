###########################################################################################
# CLASS : CPSC-449-section-1
## ASSIGNMENT: Microblogging service-twitter
## STUDENTS INFORMATION FROM Group ::
    # Nidhi Shah- 
    # Priyanka Kadam 
    # Robert Nguyen 
##########################################################################################

"""Functions this likeservice provide..
   1. User can like other users posts.
   2. Will be able to check how many likes post has recieved
   3. The list of post user has liked.
   4. View the list of popular posts.
   5. healthcheck function will support healthcheck for serviceregistry
  """
########### importing redis client modules #################################
import configparser
import logging.config
import hug
import redis
import os
import requests
import greenstalk
import json
#####################################################################
####################################################################
client = greenstalk.Client(('127.0.0.1', 11300))
#####################################################################

#Load configuration
config = configparser.ConfigParser()
config.read("./etc/api.ini")
logging.config.fileConfig(config["logging"]["config"], disable_existing_loggers=False)

# Directive for log events
hug.directive()
def log(name=__name__, **kwargs):
    return logging.getLogger(name)

#redis setup
redis_host = 'localhost'
redis_port = 6379
r = redis.StrictRedis(host = redis_host, port = redis_port, decode_responses=True)

#startup function- to register itself in service registry
@hug.startup()
def startup(api):
    url= config["service_registry_url"]["url_info"]
    pollsport= os.environ.get("PORT")
    request_url=url
    result = requests.post(request_url,data={"servicename":"likeservice","healthurl":"/health-check/","serviceport":pollsport})

###############################################################################
# healthcheck routes
@hug.get("/health-check/",status=hug.falcon.HTTP_200)
def healthchecklikeservice(response):
    print(" likeservice is available")

###############################################################################
# User will be able to like the post.
@hug.post("/newlikes/", status=hug.falcon.HTTP_201)
def like(response,postid:hug.types.number,username: hug.types.text,postauthor: hug.types.text):

    try:
        # check the author of post is not the username who is going to like the post
        if postauthor==username:
           response.status = hug.falcon.HTTP_400
           raise Exception(f"Sorry, author of post can't like own post")

        #check the post likes data already present or not-->if so, data for postid will be updated
        if(r.exists(f"post{postid}")):

            # now have to check first the username has already like the post or not
            likelist=eval(r.hgetall(f"post{postid}")['likerslist'])

            for i in likelist:
                if i==username:

                    response.status = hug.falcon.HTTP_400
                    raise Exception(f"{username} has already liked the post before")

            # this means the username is not present in like list, let's add and update the data
            likelist.append(username)
            newlist=str(likelist)
            # Now update the database with this postid-->updating a list of likers and count of likes
            r.hset(f"post{postid}","likerslist",newlist)
            r.hincrby(f"post{postid}","likeCount",1)

            # Now let's get new data of that postid
            getupdatedData = r.hgetall(f"post{postid}")

            #Adding job to the queue
            body = json.dumps({
            'postid': postid,
            'liker': username
            })
            client.use("likesasyncwork")
            client.put(body)
           
            return {"result": getupdatedData}


        # not present.. so set new data with new hash-key
        else:

            count = 0

            # create the new like data for given postid
            postData = {
                "likerslist": str([username]),
                "postID": postid,
                "author": postauthor,
                "likeCount": count+1
            }

            # after creating new like data, putting the dict object in hashmap
            r.hmset(f"post{postid}",postData)
            # ceating a list of posts
            r.rpush("posts",postid)
            getAllData = r.hgetall(f"post{postid}")
            #Adding job to the queue
            body = json.dumps({
            'postid': postid,
            'liker': username
            })
            client.use("likesasyncwork")
            client.put(body)
           
            response={"result":getAllData}
            return response

    except Exception as e:
        return {"error": str(e)}

###################################################################################
# see how many likes a post recieved
@hug.get("/postlike/{postid}", status=hug.falcon.HTTP_200)
def getpostlikes(response,postid:hug.types.number):
    try:
        #check the post likes data present or not --> if yes gather like counts
        if(r.exists(f"post{postid}")):
            likes = r.hgetall(f"post{postid}")['likeCount']
            response={"postid":postid, "likeCount": likes}
            return response
        # if the postid not present through an error
        else:
            response.status = hug.falcon.HTTP_404
            raise Exception(f" The postid {postid} does not exist or it does not have any likes, add valid postid to see the likes.")
    except Exception as e:
        return {"error": str(e)}
####################################################################################
#the list of posts which other users liked
@hug.get("/postlist/{username}", status=hug.falcon.HTTP_200)
def postlist(response,username: hug.types.text):
    try:
        lisoffpost=[]
        allpostlist=r.keys()
        # removing the posts key which collect a list of post
        allpostlist.remove('posts')
        for post in allpostlist:
            likelist=eval(r.hgetall(post)['likerslist'])
            for liker in likelist:
                if liker == username:
                    lisoffpost.append(post[-1])
        if lisoffpost:
            return {f"postids list which {username} liked": lisoffpost}
        else:
            response.status = hug.falcon.HTTP_404
            return {f"{username} liked posts": 0}
    except Exception as e:
        return {"error": str(e)}
#####################################################################################
#See the list of popular posts which has maximum likes.
@hug.get("/popularposts/", status=hug.falcon.HTTP_200)
def popularpostlist(response):
    try:
        result=[]
        # getting all keys
        allpostlist=r.keys()
        data=r.lrange('posts',0,-1)
        # shorting the posts according to the like count within most liked one will be first
        data1=r.sort('posts', by='post*->likeCount',desc=True)
        allpostlist.remove('posts')

        for i in data1:
            #for post in allpostlist:
            likes=r.hgetall(f"post{i}")['likeCount']
            likers=r.hgetall(f"post{i}")['likerslist']
            data={"postid":i,"likes":likes,"likers":likers}
            result.append(data)

        return {"result":result}

    except Exception as e:
        return {"error": str(e)}
