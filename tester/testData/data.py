from datetime import datetime

# contribution is hard coded to be a single contribution where the first user in the system is the owner
contributers =[
	{
		'contributer_id':1,
		'contributer_percentage':100
	}
]



bids =[
	{
		"tokens":60,
		"reputation":40,
		"owner":1,  # NOTE: notice that the owner user Id is according to order of users in users.json
		"contribution_id":1, # there is currently only one contribution hard coded
		"stake":10,
		"time_created":datetime.now()
	},
	{
		"tokens":40,
		"reputation":30,
		"owner":2,  # NOTE: notice that the owner user Id is according to order of users in users.json
		"contribution_id":1, # there is currently only one contribution hard coded
		"stake":10,
		"time_created":datetime.now()
	}
]
