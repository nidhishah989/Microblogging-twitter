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
import re
#import logging.config
############################3
client = greenstalk.Client(('127.0.0.1', 11300))
#############################
#####################################################################
###########################################################################################
import boto3
from boto3.dynamodb.conditions import Key

############################################################################################################
#Load configuration
config = configparser.ConfigParser()
config.read("./etc/api.ini")
dbfile = config["sqlite_timeline"]["dbfile"]
db=sqlite_utils.Database(dbfile)
###########################################################################################################3
#set clinet and resource for dynamodb
dynamoclient=boto3.client('dynamodb', region_name='us-west-2',endpoint_url="http://localhost:8000")

dynamoresource=boto3.resource('dynamodb', region_name='us-west-2',endpoint_url="http://localhost:8000")

#################################################################################################################

while(True):
    val=[]
    # this will check if any job put in the queue to work on it. The specific tube is checked out.
    client.watch("pollasyncwork")
    job = client.reserve()
    jobtodo=json.loads(job.body)
    text=jobtodo["text"]
    val.append(text)
    author=jobtodo["author"]
    regex=r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    url = re.findall(regex,text) 
    if(len(url)==0):
        
        client.delete(job)
    else:
        for x in url:
            type(x)
            
            pollid=x.rsplit('/', 1)[1]
            PollTable=dynamoresource.Table('Polls')
            response1 = PollTable.query(
                KeyConditionExpression= Key('Pollid').eq(int(pollid)))
         
            if(response1['Items']):
                print("the pollink is valid")
                client.delete(job)
            else:
                print("the polllink is not valid")
                # deletting the invalid post that shows invalid poll url
                postdata = db["post"].rows_where("Post=?",val,select=("PostID"))
                postid=""
                for i in postdata:
                    postid=i["PostID"]
                    print(i["PostID"])
                db["post"].delete(postid)
                client.delete(job)
                body = json.dumps({
                'receiveremail': f'{author}@gmail.com',
                'message': f'The polllink provided in post is not valid',
                })
                client.use('emailasyncworker')
                client.put(body)
                
