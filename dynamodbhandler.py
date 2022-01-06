###########################################################################################
## CLASS : CPSC-449-section-1
## ASSIGNMENT: Microblogging service-twitter
## STUDENTS INFORMATION FROM Group ::
    # Nidhi Shah- 
    # Priyanka Kadam 
    # Robert Nguyen 

##########################################################################################
import boto3
from boto3.dynamodb.conditions import Key

############################################################################################################

###########################################################################################################3
#set clinet and resource for dynamodb
dynamoclient=boto3.client('dynamodb', region_name='us-west-2',endpoint_url="http://localhost:8000")

dynamoresource=boto3.resource('dynamodb', region_name='us-west-2',endpoint_url="http://localhost:8000")

#################################################################################################################

# functions for creating poll, responding to poll and get result of polls
##################################################################################################################################
# this will create a new pollid every time,even though same data is given second time. becuase this is not updating poll once it created
# from front -end the timestamp will be different for each pollid
def createnewpoll(userrname,question,option1,option2,option3,option4,timestamp):
    PollTable=dynamoresource.Table('Polls')
    try:
        #check table items count
        max_key=PollTable.item_count
        PollTable.put_item(
                Item= {
                        'Pollid': (max_key+1),
                        "AuthorofPoll": userrname,
                        "options": {"Option1": {"label": option1,"votes": 0 ,"voters": []},"Option2": {"label":option2,"votes": 0,"voters": []},"Option3": {"label":option3,"votes": 0,"voters": []},"Option4": {"label": option4,"votes": 0,"voters":[]}},
                        "question": question,
                        "timestamp": timestamp
                    }
        )
        response1 = PollTable.query(
        KeyConditionExpression= Key('Pollid').eq(max_key+1))['Items']
        return {"result":response1}
    except Exception as e:
        return {"error": str(e)}

##################################################################################################################
############ updating the poll data with new pollresonder username and update pollcounts ######################
######### selectedoption is a label of the option#############
def responsetopoll(username,pollid,selectedoption):
    try:
        PollTable=dynamoresource.Table('Polls')

        # Get the authorofpoll - short key for that pollid
        response1 = PollTable.query(
            KeyConditionExpression= Key('Pollid').eq(pollid)
        )
        # get the author username here.
        pollauthor=response1['Items'][0]['AuthorofPoll']
        #check the username is not author.. cause author not allow to give poll response to him/her poll
        if(pollauthor != username):

            # find the option number dict for selected option given by user
            optioninfo= response1['Items'][0]['options']

            # get the Option number for database query using the selectedoption
            for key,v in optioninfo.items():
                if v['label']==selectedoption:
                    optionnum=key

            # Check the username has already given polls or not before updating the database
            # set the status variable to check the username have given the response to this poll
            check=0
            for key,v in optioninfo.items():
                if(username in v['voters']):
                    check=1
                    break
            if (check==1):
                raise Exception(f"{username} already have given response,only once user can give poll")

            if(check==0):
                response= PollTable.update_item(
                        Key= {
                                'Pollid': pollid,
                                'AuthorofPoll':pollauthor
                            },
                        UpdateExpression= "SET options.#select.votes= options.#select.votes + :c, options.#select.voters=list_append(options.#select.voters,:v)",
                        ExpressionAttributeNames = {'#select':optionnum},
                        ExpressionAttributeValues= {':c':1, ':v':[username]},
                        ReturnValues="UPDATED_NEW"
                )
            return {'result':response['Attributes']}
        else:
            raise Exception(f"you are the author of this, can't participate in the poll")
    except Exception as e:
        return {"error": str(e)}

##################################################################################################################################
# #############################   Get the result of polls for each options ##############################################
def getpollresult(pollid):



    # get the data from database table polls about the pollid
    try:
        PollTable=dynamoresource.Table('Polls')
        response1 = PollTable.query(
            KeyConditionExpression= Key('Pollid').eq(pollid))

        # if the pollid present ... go find the result
        if(response1['Items']):
            # gather the options dict
            optioninfo= response1['Items'][0]['options']
            # create the json for response to provide the result with percentages and how many voters with option label
            # gat the totalvotes number for this poll question
            totalvotes=optioninfo['Option1']['votes']+ optioninfo['Option2']['votes']+optioninfo['Option3']['votes']+optioninfo['Option4']['votes']

            # if the poll has recieved any votes, get other information about it's result
            if(totalvotes !=0):
                result={
                    'pollid':pollid,
                    'Question':response1['Items'][0]['question'],
                    'totalvotes':totalvotes,
                    'result':{
                        'option1':{
                            'label':optioninfo['Option1']['label'],
                            'votes':optioninfo['Option1']['votes'],
                            'votesin %':optioninfo['Option1']['votes']/totalvotes
                        },
                        'option2':{
                            'label':optioninfo['Option2']['label'],
                            'votes':optioninfo['Option2']['votes'],
                            'votesin %':optioninfo['Option2']['votes']/totalvotes
                        },
                        'option3':{
                            'label':optioninfo['Option3']['label'],
                            'votes':optioninfo['Option3']['votes'],
                            'votesin %':optioninfo['Option3']['votes']/totalvotes
                        },
                        'option4':{
                            'label':optioninfo['Option4']['label'],
                            'votes':optioninfo['Option4']['votes'],
                            'votesin %':optioninfo['Option4']['votes']/totalvotes
                        }
                    }
                }
                return result
            # for divided by zero exception -avoidance
            else:
                result= {
                    'pollid':pollid,
                    'Question':response1['Items'][0]['question'],
                    'totalvotes':totalvotes,
                    'result':{
                        'option1':{
                            'label':optioninfo['Option1']['label'],
                            'votes':optioninfo['Option1']['votes'],
                        },
                        'option2':{
                            'label':optioninfo['Option2']['label'],
                            'votes':optioninfo['Option2']['votes'],
                        },
                        'option3':{
                            'label':optioninfo['Option3']['label'],
                            'votes':optioninfo['Option3']['votes'],
                        },
                        'option4':{
                            'label':optioninfo['Option4']['label'],
                            'votes':optioninfo['Option4']['votes'],
                        }
                    }
                }
                return result
        else:

            raise Exception(f"Pollid {pollid} is not present in database")
    except Exception as e:
       return {"error": str(e)}
