
### Project: MICROBLOGGING SERVICE-TWITTER
##### CLASS PROJECT -GROUP -FALL 2021 -WEB BACK-END ENGINEERING
--------------------------------------------------------
### GOAL (PURPOSE):
 The scope of this project includes developing RESTful back-end services and preparing them for production deployment.
Our RESTful back-end services include userprofile, post-timeline, postlike, pollservice, and serviceregistry.
A second aim for this project is to address issues of scalability due to the traffic with asynchorous processes.
------------------------------------------------
#### Project Detail
To create RESTful backend services, we used the HUG framework, where JSON was used as a format for all inputs and outputs.
Userprofile and post-timeline services are implemented using a sqlite database via sqlite_utils.
Redis is used to store the likes of posts through this project's postlike service.
For pollservice, this project utilizes Amazon DynamoDB Local as a database through Boto3.
In order to manage the communication between services, a service registry has been implemented, and internal data storage is used.
A WSGI server called Gunicorn was used for production deployment preparation.
HAProxy was configured to act as a HTTP load balancer so that requests could be balanced across those instances.
The project also has asynchronous endpoints for managing scalability issues with large volumes of traffic, such as post-timeline service, likeservice, and pollservice, which use the Greenstalk library for access to the Beanstalk work queue.

------------------------------------------------------
#### PROJECT REQUIRE MODULES/libraries 

* hug
* sqlite_utils
* Requests
* json
* urllib.parse
* ruby-foreman 
* httpie
* sqlite3
* haproxy
* gunicorn
* redis
* python3-hiredis
* DynamoDBLocal
* awscli
* python3-boto3
* beanstalkd
* greenstalk
* hey
* smtplib
* threading
-----------------------------------------------------
#### project Structure
```bash
 CPSC_449_project_4_group_3_final_version
 |-CPSC449
   |--bin
      |--init.sh
   |--etc
      |--api.ini
      |--logging.ini
   |--share
      |--post.csv
      |--users.csv
   |--var
      |--post.db (created after run init.sh)
      |--users.db (created after run init.sh)
      |--log
         |--api.log
   |-- .env
   |-- Procfile
   |-- README.md
   |-- timeline.py
   |-- userprofile.py
   |-- pollservice.py
   |-- likeservice.py
   |-- serviceregistry.py
   |-- dynamodbhandler.py
   |-- emailserveron.py
   |-- emailnotifyworker.py
   |-- postworker.py
   |-- pollworker.py
   |-- likesworker.py
   |-- haproxy.group3.cfg
   |-- impact.pdf (gauging performance )
 ```


--------------------------------------------------------------
##### Project details - userprofile service
Userprofile service provide..
   1. See all users info
   2. Create a new user
   3. User accessing his/her profile
   4. Authentication of user for timeline service
   5. follow a new firend
   6. list of all firends that user is following
   7. list of all friends who follow user
   8. healthcheck function will support healthcheck for serviceregistry


--------------------------------------------------------------------
##### Project details - post-timeline service
post-timeline service provide..
   1. internal function: for user authentication- request user service
   2. Public Timeline: show all posts done by all
   3. User Timeline: show all posts that user have created( with authentication)
   4. Home Timeline: show all posts that freinds whom user follow have created (user authentication)
   5. create post: create a new post by user (user authentication)
   6. Repost: create a repost (user authentication)
   7. healthcheck function will support healthcheck for serviceregistry
   8. Postasync: will get the post details and create a new post asynchronously and synchronous work to pollworker to check the polllink validation if post is about polllink.

-------------------------------------------------------------------
#### Project details - likeservice 
likeservice provide..
   1. User can like other users posts with asyn checking post is valid or not.
   2. Will be able to check how many likes post has recieved
   3. The list of post user has liked.
   4. View the list of popular posts.
   5. healthcheck function will support healthcheck for serviceregistry

-----------------------------------------------------------------
#### Project details - pollservice
pollservice provide..
   1. Create a poll -with one question and four options
   2. Participate in poll - give a response
   3. View the result of polls
   4. healthcheck function will support healthcheck for serviceregistry


--------------------------------------------------------------------
#### Project details - serviceregistry
 Service Registry provides..
   1. Registers all services and keeps track of service name, URL, and port port number
   2. Conducts health checks on services
   3. help one service instances to communicate with other service instance by providing service port information.
--------------------------------------------------------------------
#### project details- dynamodbhandler.py
This files is used to query the dynamodb table -Polls, which will be created under us-west-2 region by init.sh file

The file will connect with dynamodb table Polls on port 8000 and run all queries to support the pollservice functions.

--------------------------------------------------------------------
#### Project details - emailserveron.py
This file starts a SMTP Debugging Server on a specified port.
In our case it is 1025.

--------------------------------------------------------------------
#### Project details - emailnotifyworker.py
This file will handle asynchronously notifying the user when a post or like has not been accepted. It will then display 
the information on the console.

--------------------------------------------------------------------
#### Project details - postworker.py
This file is a worker file that add post in database asynchronously

-------------------------------------------------------------------
#### Project details - pollworker.py
This file is a worker file that check the post has polllink reference, if so, is it valid or not

--------------------------------------------------------------------
#### Project details - likesworker.py

This file is a worker file that check the like for invalid post or not
-------------------------------------------------------------------
#### How to test an example run for this project:

1. ##### for dynamodb database setup..
   1) Open new terminal- open the folder where dynamodb downladed.
      Note: we use "US West (Oregon) Region" dynamodb version
            Configuration used: same as provided in the project 3 document
                              AWS Access key ID :fakeMykeyId
                              AWS Secreat Access Key [None] : fakeSecretAccessKey
                              Default region name [None] : us-west-2
                              Default output format [None]: table
   2)In that opend folder in terminal, run :
            java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar
            Note: This will run dynamodb on 8000 port
   

2. ##### SETUP all desinged database by running init.sh...
   1. Open up a command-line terminal, and navigate to CPSC449 directory in which bin directory placed, the 'init.sh' file is in the bin directory
   2. Run the command in /CPSC449$ :

            ./bin/init.sh

      Note: If the access denied. run command " chmod +x ./bin/init.sh " and try again ./bin/init.sh

      Note: Two database named users.db and post.db will be created under /var/ directory and Polls table will be created under us-west-2 region.
      Note: if the Polls table already exists, delete it using following command
      aws dynamodb delete-table --table-name Polls --region us-west-2 --output json --endpoint-url http://localhost:8000/
            **users.db (tables: users and followers) with users information inserted in users table and with empty followers table

            post.db (tables: post and repost) with post information inserted in the post table and with empty repost table

            Polls table of dynamodb- Pollid is primary key and AuthorofPoll is short key in table
            Note: for this project, we did not have setup any secondary global index **

3. ##### foreman -WSGI-Gunicorn -to run the application
After creating database run the application using same terminal for following command:

           foreman start -m "serviceregistry=1,userprofile=1,timeline=3,likeservice=1,pollservice=1,postworker=1,likesworker=1,pollworker=1,emailserveron=1,emailnotifyworker=1"


   Note: The gunicorn command will find PORT in .env file
   According to that,
   serviceregistry will be on port 5000
   userprofile will be on port 5100
   timeline.1 will be on port 5200
   timeline.2 will be on port 5201
   timeline.3 will be  on port 5202
   likeservice will be on port 5300
   pollservice will be on port 5400

 -------------------------------------------------------------------
4. ##### userprofile service testing..
   1. To check all users open browser, we have used firefox

      http://localhost:5100/users/

   2.  If user is checking a userprofile, open browser

      command: http://localhost:5100/users/username

      provide username, example:

      http://localhost:5100/users/falgun12

   3. To create new user, open a new command-line terminal
      example:

               http POST localhost:5100/newuser/ username=rohit email=rohit@gmail.com password=rohit1234 Bio=Artist


   4.  To add a follower, in command-line terminal

      example1:

         http POST localhost:5100/follow/ username=falgun12 friendprofilename=salin followdate=10/21/2021

      example2:

      http POST localhost:5100/follow/ username=donal34 friendprofilename=salin followdate=10/21/2021

      example3:

      http POST localhost:5100/follow/ username=rohit friendprofilename=falgun12 followdate=10/21/2021

      example4:

      http POST localhost:5100/follow/ username=falgun12 friendprofilename=donal34 followdate=10/21/2021

   5. To check the list of users followed by user, open a browser

      example: http://localhost:5100/following/falgun12

   6. To see the list of user's friends who follow users, open a browser

      example: http://localhost:5100/yourfollowers/salin

--------------------------------------------------------------------
5. ##### post-timeline service testing..  (use Firefox browser)

   1. To check the publictimeline, open a browser

      http://localhost:5200/publictimeline/

      If want to run in command line terminal,

      http GET localhost:5200/publictimeline/

   2. To check the usertimeline, open a browser

      http://localhost:5202/usertimeline/falgun12

      The login page will get open, provide the username as falgun12 and password as falgun1234
      The command to run in terminal:

      http --auth falgun12:falgun1234 GET localhost:5201/usertimeline/falgun12

   3. To check the hometimeline, open a terminal
      Run a following command to get following friend's list from userprofile

      friends=$(http GET localhost:5100/following/falgun12)

      Now, call the hometimeline. with that friends list:

      http --auth falgun12:falgun1234 POST localhost:5201/hometimeline/ username=falgun12 friends="$friends"

   4. To create a new post, open a terminal
      Run a command:

      http --auth falgun12:falgun1234 POST localhost:5202/createpost/ username=falgun12 post="hi, falgun again" posttimestamp="12/3/2021, 8:00"

   5. To repost a post, open a terminal
      Run a command:

      http --auth falgun12:falgun1234 POST localhost:5202/repost/ username=falgun12 actualpostid=8 repost="hi, this is falgun again" posttimestamp="12/3/2021, 9:00"

   6. To create a post , asynchronously
      http --auth falgun12:falgun1234 POST localhost:5202/addpostasync/ username=falgun12 post="hi, falgun again from async" posttimestamp="12/3/2021, 8:00"

--------------------------------------------------------------------
6. ##### postlike service testing...
   1. To like a post, open a terminal
      Run a command:

      http POST localhost:5300/newlikes/ postid=1 username=riya postauthor=falgun12
      
   2. To check how many likes a post received, open a terminal
      Run a command:

      http://localhost:5300/postlike/1
   
   3. To check list of posts that users liked, open a terminal
      Run a command:

      http://localhost:5300/postlist/falgun12
   
   4. To check popular posts, open a terminal
      Run a command:

      http://localhost:5300/popularposts

--------------------------------------------------------------------
7. ##### pollservice service testing..
   NOTE: SHOULD BE DYNAMODB RUNNING ON 8000 port TO RUN FOLLOWING COMMANDS
   1. Create a poll -with one question and four options
      Run a command in terminal:
      http POST localhost:5400/newpoll/ username=falgun12 question="What is your favorite color?" option1=red option2=yellow option3=black option4=white timestamp="11/26/2021 19:51"
      
   2. Participate in poll- give your response to poll
      Run a command in terminal:
      http POST localhost:5400/pollpart/ username=donal34 pollid=1 selectedoption=yellow

      http POST localhost:5400/pollpart/ username=salin pollid=1 selectedoption=black
      

   3. To see poll result 
      Run in browser:
      
         http://localhost:5400/pollresult/1

8. ##### Service Registry -----
Service Registry have three routes and one startup function
   register : This route function will be called from all servies from its startup function, It will register services in serviceregistry
   startup  : This function will run once when the serviceregistry call first time. It will create the thread for healthcheck usage in future
   getserviceurl : This function will run when one service (example: timeline) need other service instance information(example:userprofile).
                   It will check the service instance registered or not, if yes, provides the service instance port.
                   If no, it provides 409 error for 502 BAD gateway error raise
   healthcheck: This function will use thread to do healthcheck of registered services in time manner, if something wrong it will do locking.

   How healthcheck and threding works?
   - First, the service will register to serviceregistry, and it starts the deamon thread.
   - The thread will check the register servies health every 10 seconds
   - In the foreman terminal, the output of healthcheck from each service will print "{servicename} is available" and sends 200 status to serviceregistry.


9. ##### LOAD BALANCING ------
   RUNNING APPLICATION THROUGH HAPROXY  (use Firefox browser)

   1. Configuration file for haproxy: haproxy.group3.cfg
   2. Copy the content from haproxy.group3.cfg file to your haproxy file (location: /etc/haproxy/haproxy.cfg)
   3. Add lines specially after default in your haproxy.cfg file as below

   4. Restart the haproxy service
   5.Now run all above endpoints of userprofie and timeline service with
   localhost:80/ endpoints...
   as specified places(browser or terminal)
   6. also Check the stat in browser:
      with http://localhost:80/haproxy?stats


10. ##### Additional asynchronous endpoint testing..
     RUNNING postworker for creating a new post asynchronously  

11. ##### Hey testing ------
   hey testing with authentication for synchronous(createpost) and asynchronous(addpostasync) endpoints of timeline

   **** NOTE: DUE TO SERVICEREGISTRY SETTING, FIRST  TIME FOLLOWING COMMAND RUN WILL THROUGH 502 STATUS ERROR DUE TO UNREGISTERED USERPROFILE INSTANCE
            RUN THE http://localhost:5100/users/   t register the userprofile
            and than run following commands
   For synchronous (createpost) command:
   hey -n 10 -c 10 -H "Authorization: Basic $(echo -n salin:salin1234 | base64)" -H "Content-Type: application/json" -m POST -d '{"username":"salin","post":"this is syn testing","posttimestamp":"12/3333"}' http://127.0.0.1:5200/createpost/

   For asynchronous (addpostasync) endpoint command:
   hey -n 10 -c 10 -H "Authorization: Basic $(echo -n donal34:donal1234 | base64)" -H "Content-Type: application/json" -m POST -d '{"username":"donal34","post":"this is donal asyn from hey","posttimestamp":"12/17/2021 14:55"}' http://127.0.0.1:5200/addpostasync/ 

   For asynchronous (addpostasync) endpoint to check the pollworker task for validation of poll url in post command:
   hey -n 10 -c 10 -H "Authorization: Basic $(echo -n donal34:donal1234 | base64)" -H "Content-Type: application/json" -m POST -d '{"username":"donal34","post":"this is url http://localhost:5300/pollresult/120","posttimestamp":"12/17/2021 14:55"}' http://127.0.0.1:5200/addpostasync/ 
   
   ###### HEY result ---
 We have captured the results and store in impact.pdf file 

12. ##### Backgroud Processing tsting-------
      1. Likeworker addded for validation of the post
      Test: 
      run this command in the terminal and see the emailnotifyworker prints  the email details in foreman window
            http POST localhost:5300/newlikes/ postid=120 username=riya postauthor=falgun12

      run this command in the terminal and see the emailnotifyworker prints the email details in foreman window
               http --auth falgun12:falgun1234 POST localhost:5202/addpostasync/ username=falgun12 post="this is url http://localhost:5300/pollresult/124" posttimestamp="12/3/2021, 8:00"

      2. pollworker added for validation of poll link in post-timeline
      Notifying users --- IF there are invalid post like or a poll url , notify user via email.

---------------------------------------------------------
##### Student INFORMATION -FALL 2021 -WEB BACK-END ENGINEERING
Nidhi Shah
Priyanka Kadam 
Robert Nguyen