###########################################################################################
## CLASS : CPSC-449-section-1
## ASSIGNMENT: Microblogging service-twitter
## STUDENTS INFORMATION FROM Group ::
    # Nidhi Shah- 
    # Priyanka Kadam 
    # Robert Nguyen 

##########################################################################################

"""Functions this user service provide..
   1. See all users info
   2. Create a new user
   3. User accessing his/her profile
   4. Authentication of user for timeline service
   5. follow a new firend
   6. list of all firends that user is following
   7. list of all friends who follow user
   8. healthcheck function will support healthcheck for serviceregistry"""
########### imporitng require modules #################################
import configparser
import logging.config
import hug
import sqlite_utils
import os
import requests
#####################################################################

#Load configuration
config = configparser.ConfigParser()
config.read("./etc/api.ini")
logging.config.fileConfig(config["logging"]["config"], disable_existing_loggers=False)


#A Directive for Sqlite database- for users.db (tables: users and followers)
@hug.directive()
def sqlite(section="sqlite", key="dbfile", **kwargs):
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
    result = requests.post(request_url,data={"servicename":"userprofile","healthurl":"/health-check/","serviceport":pollsport})
# Routes
###############################################################################
# healthcheck routes
@hug.get("/health-check/",status=hug.falcon.HTTP_200)
def healthchecklikeservice(response):
    print(" userprofile is available")
#######################################################################
# Get All users information
@hug.get("/users/")
def users(db: sqlite):
    return {"users": db["users"].rows_where(select="userid,username,email,Bio")}

##############################################################################
# checking the user authentication
@hug.get('/authentication/{username}')
def authenticateuserprofile(response,username: hug.types.text, db: sqlite):
    """
    Authenticate username with a database
    :param username:
    :return: autheticated user profile
    """
    authresult={}
    val=[]
    val.append(username)
    #database query
    user = db["users"].rows_where("username=?",val,select=("username,password"))
    # if there is user.catch user's login info
    for i in user:
        authresult["username"]=i["username"]
        authresult["password"]=i["password"]
    #check the user found or not
    if authresult=={}:
        response.status=hug.falcon.HTTP_401  #error as user not authorized
    else:
        # user's username was good, authorized. send user's object
        return authresult

####################################################################################################################
# add new user -create user
@hug.post("/newuser/", status=hug.falcon.HTTP_201)
def create_user(response,username: hug.types.text,email: hug.types.text,password: hug.types.text,Bio:hug.types.text,db: sqlite):
    users = db["users"]
    user = {
        "username": username,
        "email": email,
        "password": password,
        "Bio": Bio,
    }

    try:
        #add new user
        users.insert(user)
        user["userid"] = users.last_pk
    except Exception as e:
        response.status = hug.falcon.HTTP_409
        return {"error": str(e)}

    response.set_header("Location", f"/users/{user['userid']}")
    return user

##########################################################################################
# show perticular user's information- profile info
@hug.get("/users/{username}")
def retrieve_user(response, username: hug.types.text, db: sqlite):
    users = []
    val=[]
    try:
        val.append(username)
        #database query
        user = db["users"].rows_where("username=?",val)
        users.append(user)
    except sqlite_utils.db.NotFoundError:
        response.status = hug.falcon.HTTP_404
    return {"users": users}

##################################################################################################
#Add new follower in user's list
""" this will allow user to follow a friend,
    The user and freindprofile will be checked fisrt as it is correct or not
    Check: user is not trying to follow ownself.
    Check: user is already a friend with person
    Do: New frined,, update the followers table in database"""
@hug.post("/follow/",status=hug.falcon.HTTP_201)
def follownewfriend(response,username:hug.types.text,friendprofilename:hug.types.text,followdate:hug.types.text,db:sqlite,):
    follower=db["followers"]
    values=[]
    val=[]
    userval=[]

    try:
        #try to find the user in the users table first before following start, throw exception
        userval.append(username)
        userdata = db["users"].rows_where("username=?",userval,select="userid")
        #user found, now insert the follow row with userid as forignkey.
        #checking the user is not trying to be firend to ownself
        user=next(userdata,None)
        if username != friendprofilename:
            try:

                #now find the firendprofilename in the users table,
                values.append(friendprofilename)

                #get the firend id if the friend exist
                firend=db["users"].rows_where("username=?",values,select="userid")
                # check the user is following the friend already or not
                val.append(user["userid"])
                findfollow=db["followers"].rows_where("followerid=?",val,select="followername")

                # generator object iteration for record, if record is there, create the follower record.,else,throw exception
                f=next(firend,None)
                if f is not None:

                    # find that the user is already following this new freind or not
                    for i in findfollow:

                        if(i['followername']==friendprofilename):
                            raise Exception(f"you are already following {friendprofilename}")
                    #new following.. add noww
                    followto={"followerid":user["userid"],"followername":friendprofilename,"followdate":followdate}
                    follower.insert(followto)
                    followto["id"] = follower.last_pk
                    return f"you are following {friendprofilename} from now."
                 #throw an exception if there is no record of firend
                else:
                    raise Exception(f"Unsuccessful attempt in finding {friendprofilename}. Confirm the freind's profilename")

            except Exception as e:
                response.status = hug.falcon.HTTP_409
                return {"error": str(e)}
        #throw exception for trying to be friend ownself
        else:
            raise Exception(f"No need to follow yourself to use this service.")
    except sqlite_utils.db.NotFoundError:
        response.status=hug.falcon.HTTP_404
        return {f"Login require."}
    except Exception as err:
        response.status = hug.falcon.HTTP_409
        return {"error": str(err)}

#################################################################################################
# get list of friends you are following
""" The funtion will provide a list of firends that user follow
    Check: the user exist or not
    Check: is user following anyone
    Do: if user following, then provide a list of following friends"""
@hug.get("/following/{username}")
def find_following(response, username: hug.types.text, db: sqlite):
    val=[]
    follow=[]
    firends={}
    try:
        val.append(username)
        #get the user id if the user exist
        user=db["users"].rows_where("username=?",val,select="userid")
        userres=next(user,None)
        if userres is None:
            raise Exception(f"The user does not exist.")
        else:
            follow.append(userres["userid"])
            #database query to find all following friends that user follow
            followingfriendlist=db["followers"].rows_where("followerid=?",follow,select="followername")
            j=1
            for i in followingfriendlist:
                firends[f'firend{j}']=i["followername"]
                j=j+1

            #not following anyone...raise exeption
            if len(firends)==0:
                raise Exception (f"Username {username} not following anyone.")
            else:
                #return the list of friends taht user follow
                return firends
    except Exception as err:
        response.status=hug.falcon.HTTP_409
        return {"error": str(err)}

#########################################################################################
# get list of firends who follow you
"""This function will give a list of frineds who follow user
   Check: is any firend follow  the user
   Do: if found friends who follow user, give a list from database"""
@hug.get("/yourfollowers/{username}")
def find_followers(response, username: hug.types.text, db: sqlite):
    value=[]
    myfollower={}
    try:
        value.append(username)
        # get all followers ids from followers if anyone is following this user
        userfollowers=db["followers"].rows_where("followername=?",value,select="followerid")
        j=1
        for i in userfollowers:
            myfollower[f'follower{j}']=db["users"].get(i["followerid"])["username"]
            j=j+1
        if(len(myfollower)==0):
            raise Exception (f"Username {username} does not have any followers.")
        else:
            return {"followers":myfollower}
    except Exception as err:
        response.status=hug.falcon.HTTP_409
        return {"error": str(err)}
###############################################################################
