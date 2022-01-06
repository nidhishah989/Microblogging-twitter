###########################################################################################
# CLASS : CPSC-449-section-1
## ASSIGNMENT: Microblogging service-twitter
## STUDENTS INFORMATION FROM Group ::
    # Nidhi Shah- 
    # Priyanka Kadam 
    # Robert Nguyen 

##########################################################################################

import smtplib
import greenstalk
from smtplib import SMTP
import json

client = greenstalk.Client(('127.0.0.1', 11300))

fromaddr = "project4twitter@notification.com"


while(True):
    # this will check if any job put in the queue to work on it. The specific tube is checked out.
    client.watch("emailasyncworker")
    job = client.reserve()
    print(job.id)
    jobtodo = json.loads(job.body)
    msg = jobtodo["message"]
    toaddr = jobtodo["receiveremail"]

    server = smtplib.SMTP('127.0.0.1', 1025)
    server.set_debuglevel(True)
    server.sendmail(fromaddr,toaddr , msg)
    server.quit()
    client.delete(job)
