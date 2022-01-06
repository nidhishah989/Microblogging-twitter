#!/bin/sh
########################## user database -(table: users, followers)
sqlite-utils insert ./var/users.db users --csv ./share/users.csv --detect-types --pk=userid
sqlite-utils create-index ./var/users.db users username email password --unique


sqlite-utils create-table ./var/users.db followers\
      id integer\
      followerid integer \
      followername text \
      followdate text \
      --pk id\
      --fk followerid users userid \
      --fk followername users username

sqlite-utils tables ./var/users.db --schema -t

########################## post database -(table: post, repost)
sqlite-utils insert ./var/post.db post --csv ./share/post.csv --detect-types --pk=PostID

sqlite-utils create-table ./var/post.db repost\
      repostid integer \
      username integer \
      repost text \
      actualpostid integer \
      reposttimestamp text \
      --pk repostid \
      --fk username post AuthorName \
      --fk actualpostid post PostID

sqlite-utils tables ./var/post.db --schema -t

#########################################################
################# dynamodb- poll database setup #############
##### Pollid - partition key, AuthorofPoll - short key #########
#### NOTE: 
###

aws dynamodb create-table \
    --table-name Polls \
    --attribute-definitions \
        AttributeName=Pollid,AttributeType=N \
        AttributeName=AuthorofPoll,AttributeType=S \
    --key-schema \
        AttributeName=Pollid,KeyType=HASH \
        AttributeName=AuthorofPoll,KeyType=RANGE \
    --provisioned-throughput \
        ReadCapacityUnits=10,WriteCapacityUnits=5\
    --region us-west-2 \
    --output json \
    --endpoint-url http://localhost:8000