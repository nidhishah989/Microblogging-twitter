###########################################################################################
# CLASS : CPSC-449-section-1
## ASSIGNMENT: Microblogging service-twitter
## STUDENTS INFORMATION FROM Group ::
    # Nidhi Shah- 
    # Priyanka Kadam 
    # Robert Nguyen 

##########################################################################################

"""Functions this pollservice provide..
   1. Create a poll -with one question and four options
   2. Participate in poll - give a response
   3. View the result of polls
   4. healthcheck function will support healthcheck for serviceregistry
  """
########### imporitng require modules #################################
import os
import configparser
import logging.config
import hug
import dynamodbhandler as databasedynamo
import requests

#####################################################################

#Load configuration
config = configparser.ConfigParser()
config.read("./etc/api.ini")
logging.config.fileConfig(config["logging"]["config"], disable_existing_loggers=False)

# Directive for log events
hug.directive()
def log(name=__name__, **kwargs):
    return logging.getLogger(name)

@hug.startup()
def startup(api):
    url= config["service_registry_url"]["url_info"]
    pollsport= os.environ.get("PORT")
    request_url=url
    result = requests.post(request_url,data={"servicename":"pollservice","healthurl":"/health-check/","serviceport":pollsport})


# Routes
########################################################
# healthcheck routes
@hug.get("/health-check/",status=hug.falcon.HTTP_200)
def healthchecklikeservice(response):
    print(" pollservice is available")
#######################################################################
# Create a poll -with one question and four options
@hug.post("/newpoll/", status=hug.falcon.HTTP_201)
def createnewpoll(response,username: hug.types.text,question: hug.types.text,option1: hug.types.text,option2:hug.types.text,option3:hug.types.text,option4:hug.types.text,timestamp:hug.types.text):
    result= databasedynamo.createnewpoll(username,question,option1,option2,option3,option4,timestamp)
    # checking if there is an error.. through 400 status code
    if "error" in result:
        response.status = hug.falcon.HTTP_400
    return result

#########################################################################
# Participate in poll- give your response to poll
@hug.post("/pollpart/",status=hug.falcon.HTTP_201)
def participantinpoll(response,username:hug.types.text,pollid:hug.types.number,selectedoption:hug.types.text):

    result=databasedynamo.responsetopoll(username,pollid,selectedoption)
    # checking if there is an error.. through 400 status code
    if "error" in result:
        response.status = hug.falcon.HTTP_400
    return result

########################################################################
# poll result- with pollid
@hug.get("/pollresult/{pollid}",status=hug.falcon.HTTP_200)
def viewpollresult(response,pollid=hug.types.number):
    result=databasedynamo.getpollresult(int(pollid))
    if "error" in result:
        response.status = hug.falcon.HTTP_409
    return result
