from datetime import datetime

# contribution is hard coded to be a single contribution where the first user in the system is the owner
# NOTE: notice that the contributer_id is according to order of users in users.json

contributers =[
	{
		'contributer_id':1,
		'contributer_percentage':100
	}
]


# NOTE: notice that the owner user Id is according to order of users in users.json
bids =[
	{
		"tokens":60,
		"reputation":100,
		"owner":1,  
		"contribution_id":1, 
		"stake":100,
		"time_created":datetime.now()
	},
	{
		"tokens":40,
		"reputation":100,
		"owner":2,  
		"contribution_id":1, 
		"stake":100,
		"time_created":datetime.now()
	}
]
