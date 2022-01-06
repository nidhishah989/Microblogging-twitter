###########################################################################################
# CLASS : CPSC-449-section-1
## ASSIGNMENT: Microblogging service-twitter
## STUDENTS INFORMATION FROM Group ::
    # Nidhi Shah- 
    # Priyanka Kadam 
    # Robert Nguyen 
##########################################################################################

""" Service Registry file
    1. Registers all services and keeps track of service name, URL, and port port number
    2. Conducts health checks on services
    3. help one service instances to communicate with other service instance by providing service port information.

"""
from falcon import status_codes
import hug
import requests
import logging
import threading
import time
import concurrent.futures
import socket

registeredservices={}

@hug.startup()
def startup(api):
    my_thread = threading.Thread(target=healthcheck, args=())
    my_thread.setDaemon(True)
    my_thread.start()

###################################################################
def healthcheck():
    lock = threading.Lock()
    print(registeredservices)

    while True:
        for k,v in registeredservices.items():
            healthurl=registeredservices[k]['healthcheckurl']
            respond = requests.get(healthurl)
            print (respond.status_code)
            if respond.status_code!= 200:
                print("Locking thread")
                lock.acquire()
                del registeredservices[k]
                print("Unlocking thread")
                lock.release()


        time.sleep(10)

######################################################
# this function will help all services to register them in serviceregistry
@hug.post("/register/",status=hug.falcon.HTTP_201)
def register(response,servicename=hug.types.text,healthurl=hug.types.text,serviceport=hug.types.text):

    if(servicename not in registeredservices.keys()):

        registeredservices[servicename]={'port': serviceport, 'healthcheckurl':f'http://localhost:{serviceport}{healthurl}'}
        print(registeredservices[servicename])
        print(registeredservices[servicename]['port'])
    else:
        response.status = hug.falcon.HTTP_409


######################################################
#this function will help all services to find other service port information
@hug.get("/getserviceurl/{servicename}",status=hug.falcon.HTTP_200)
def getserviceurl(response,servicename=hug.types.text):
    # check register services dictionary not empty.
    if registeredservices:
        # check the servicename instance is available in registered services
        if servicename in registeredservices.keys():
            port=registeredservices[servicename]['port']
            return {'portnumber': port}
        else:
            response.status=hug.falcon.HTTP_409
