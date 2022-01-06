###########################################################################################
# CLASS : CPSC-449-section-1
## ASSIGNMENT: Microblogging service-twitter
## STUDENTS INFORMATION FROM Group ::
    # Nidhi Shah- 
    # Priyanka Kadam 
    # Robert Nguyen 

##########################################################################################

import greenstalk
import os
import json
import time
import hug
import redis
import configparser
import sqlite_utils

#import logging.config
############################3
client = greenstalk.Client(('127.0.0.1', 11300))
#############################
#####################################################################
#Load configuration
config = configparser.ConfigParser()
config.read("./etc/api.ini")
dbfile = config["sqlite_timeline"]["dbfile"]
db=sqlite_utils.Database(dbfile)

#redis setup
redis_host = 'localhost'
redis_port = 6379
redisdb = redis.StrictRedis(host = redis_host, port = redis_port, decode_responses=True)

while(True):
    users=[]
    # this will check if any job put in the queue to work on it. The specific tube is checked out.
    client.watch("likesasyncwork")
    job = client.reserve()
    jobtodo=json.loads(job.body)
    posts=db["post"]

    try:
        #Checking post id is valid or not
        # take all datas from job body
        postid=jobtodo["postid"]
        liker=jobtodo["liker"]
        try:

            data=db["post"].get(postid)
            client.delete(job)


        #no post found, the user get notified via email.
        except sqlite_utils.db.NotFoundError:
            #email function goes here
            client.delete(job)
            body = json.dumps({
            'receiveremail': f'{liker}@gmail.com',
            'message': f'The user id trying to like a invalid post',
            })
            client.use('emailasyncworker')
            client.put(body)
            #Deleting invalid data in likeservice
            redisdb.delete(f"post{postid}")

    except Exception as e:
        #Job is not done, some error comes in it. so put job back and retried it later
        client.release(job,delay=4)
