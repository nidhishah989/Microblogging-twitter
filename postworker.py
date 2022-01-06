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
import configparser
import sqlite_utils
import sys
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

while(True):
    # this will check if any job put in the queue to work on it. The specific tube is checked out.
    client.watch("postasyncwork")
    job = client.reserve()
    jobtodo=json.loads(job.body)
    posts=db["post"]
    try:
        # take all datas from job body
        post=jobtodo["postdata"]
        posttimestamp=jobtodo["timeline"]
        author=jobtodo["username"]

        # gather all information that need to insert in the database table -post
        postdata={"Post":post,"PostTimestamp":posttimestamp,"AuthorName":author}
        posts.insert(postdata)
        postdata["PostID"]=posts.last_pk
        # job is done , so delete it
        client.delete(job)
    except Exception as e:
        #Job is not done, some error comes in it. so put job back and retried it later
        client.release(job,delay=4)
