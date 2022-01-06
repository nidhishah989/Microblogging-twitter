###########################################################################################
# CLASS : CPSC-449-section-1
## ASSIGNMENT: Microblogging service-twitter
## STUDENTS INFORMATION FROM Group ::
    # Nidhi Shah- 
    # Priyanka Kadam 
    # Robert Nguyen 

##########################################################################################

import smtpd
import asyncore
import sys
import os

server = smtpd.DebuggingServer(('127.0.0.1', 1025), None)
asyncore.loop()
