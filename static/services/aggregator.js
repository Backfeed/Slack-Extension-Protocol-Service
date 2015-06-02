angular.module('MyApp')
	.factory('Const', function($http) {

	  return {
	    	NODE_TYPE_BOARD:'skill',
			NODE_TYPE_PERSON:'person',
			NODE_TYPE_TASK:'interest',
			NODE_TYPE_LIST:'internship'
	  };

	})
	.factory('Filter', function($http) {
		var lastCommand;
		
		var filterData  = [{type:'Boards',selected:false,style:' filter-boards',styleUnselected:'filter-button'},{type:'Lists',selected:false,style:'filter-button',styleUnselected:'filter-button'},{type:'Tasks',selected:false,style:'filter-button',styleUnselected:'filter-button'},{type:'Users',selected:false,style:'filter-users',styleUnselected:'filter-button'}];
		

	  return {
		getData:function(){
			return filterData;
		},
		setData:function(data){
			
			filterData = data;
		},
		// TBD: change numbers to enum:
		boardsIsActivated: function() {
	      return filterData[0].selected;
	    },
		listsIsActivated: function() {
	      return true;
	    },
		tasksIsActivated: function() {
	      return true;
	    },
	    usersIsActivated: function() {
	      return filterData[3].selected;
	    },
	    feedbackIsActivated: function() {
	      return true;
	    }
	  };

	})
	.factory('Feedback', function($http) {


		 return {
		   
		   }
		 
	})
	.factory('Users', function($http,Const) {
		 console.log('loading Users into system.');
		 var users
		
		var setUsers =	function (usersIn) {
				for (i in usersIn){
					usersIn[i].type = Const.NODE_TYPE_PERSON;
				}
				users = usersIn;
		}
			
		
		//var users = $http.get('/api/users');
		/*
	 	$http.get('/api/deapusers').
		  success(function(data, status, headers, config) {
		    // this callback will be called asynchronously
		    // when the response is available
		 			
		
				setUsers(data.json_list);
				console.log('users loaded:');
				console.dir(users);		  
			}).
		  error(function(data, status, headers, config) {
		    // called asynchronously if an error occurs
		    // or server returns response with an error status.
			console.log('Users:get deap Users:error:'+data);
		  });
		*/

		 return {
		   	setUsers: setUsers,
		    getUsers: function() {
		     	return users;
		   }
		 }
	})
	.factory('Tasks', function($http,Filter,Account,Const,Users) {
		var orgName = 'lazooznew';
		var token = undefined;
		var onBoardsReadyCB;
		var onListsReadyCB;
		
		// data state:
		var boardData = {id:'',displayName:'dummy',lists:[],type:Const.NODE_TYPE_BOARD}; 
		
		
		
		
		function getListsByBoardId(onSuccess,onError,boardId) {
			
			// set state:
			onListsReadyCB = onSuccess;
			boardData = {id:boardId,displayName:'dummy',lists:[],type:Const.NODE_TYPE_BOARD} 
			
			var HOST = 'api.trello.com';
			var PROTOCL = 'https://';
			var TOKENS_SERVICE = '/1/boards/'+boardId+'/lists';

			var url = PROTOCL + HOST + TOKENS_SERVICE;
			console.log('url:'+url);

			var token = Account.getUserData().trello;
			var key = 'c1bb14ae5cc544231959fc6e9af43218';
			var data = {
				token:token,
				key:key
			}

			// TBD: move to use angularJS instead of Jquery and get rid of need to change  Host when we deploy...
			// TBD: which API ? do we get 'my borads or boards of orgenziation'
			$.ajax({
				type: "GET",
			  url: url,
			  data: data,
			  success: parseLists,
				persist:true,
				dataType:'JSON'
			});
		}
		
		function parseLists(listsResult) {
			console.log('reveiced listsResult:');
			console.log(listsResult);
			
			var board = {id:'',displayName:'dummy',lists:[],type:Const.NODE_TYPE_BOARD}; 
			
			
			// parse and fill in listsData:
			for (var i = 0; i < listsResult.length; i++) {
	
			    var listRes = listsResult[i];
				
				// get current board Id:
				boardData.id = listRes.idBoard;
			
				//var newList = {id:listRes.id,displayName:listRes.name,type:Const.NODE_TYPE_LIST} ;
				
				boardData.lists.push({id:listRes.id,displayName:listRes.name,type:Const.NODE_TYPE_LIST});
				
			}
			
			// publish:	
			console.log('finished parsing lists:');
			console.dir(boardData	)	;
			onListsReadyCB([boardData]);	
		}
		
		
		function getBoards(onSuccess,onError,type) {
			
			onBoardsReadyCB = onSuccess;
			
			
			// TBD: use Filter service to collect the relevent data:
			
			// get boards:
			// TBD:  Trello Client?
			//https://api.trello.com/1/members/me/boards?key=c1bb14ae5cc544231959fc6e9af43218&token=3ba3e4e6adc7b88695c2364743479c75f5f3d20080c44a6aef49673bdbe3456a
			//Trello.organizations.get(orgName, parseBoards, boardsFailed);

			// TBD: get token from User service 
			//var token = '3ba3e4e6adc7b88695c2364743479c75f5f3d20080c44a6aef49673bdbe3456a';
			
			/*
			$http.get('api.trello.com/1/members/me/boards', {'key':key,'token':token}).
			  success(function(data, status, headers, config) {
			    // this callback will be called asynchronously
			    // when the response is available
					//this.onReadyCB(data);
			  }).
			  error(function(data, status, headers, config) {
			    // called asynchronously if an error occurs
			    // or server returns response with an error status.
				console.log('Tasks:getBoards:error:'+data);
			  });
			*/
			
			
			var HOST = 'api.trello.com';
			var PROTOCL = 'https://';
			var TOKENS_SERVICE = '/1/organizations/backfeed/boards';

			var url = PROTOCL + HOST + TOKENS_SERVICE;
			console.log('url:'+url);

			var token = Account.getUserData().trello;
			var key = 'c1bb14ae5cc544231959fc6e9af43218';
			var data = {
				token:token,
				key:key
			}

			// TBD: move to use angularJS instead of Jquery and get rid of need to change  Host when we deploy...
			// TBD: which API ? do we get 'my borads or boards of orgenziation'
			$.ajax({
				type: "GET",
			  url: url,
			  data: data,
			  success: parseBoards,
				persist:true,
				dataType:'JSON'
			});
			
	    };
	
		function parseBoards(boardsResult) {
			console.log('parseBoards: trello boardsResult:');
			console.dir(boardsResult);
			
		    var boards = [];
								
			// parse and fill in boardsData:
			for (var i = 0; i < boardsResult.length; i++) {
			    var boardRes = boardsResult[i];
				var newBoard = {id:boardRes.id,displayName:boardRes.name,members:[],type:Const.NODE_TYPE_BOARD} 
				
				// get board members:
				var members = boardRes.memberships;
				for (var j = 0; j < members.length; j++) {
					var memberRes = members[j];
					var member = {id:memberRes.idMember,displayName:"None Deap User",type:Const.NODE_TYPE_PERSON};
					
					// change User Ids to Deap Ids on User Nodes:
					normelizedUser = normelizeUserNode(member);
					
					if(!normelizedUser){
						// if user not registereed in deap use as non register member:
						normelizedUser = member;
						
						// TBD: should we show non deap members ?
						//newBoard.members.push(normelizedUser);
					}
					else{
						newBoard.members.push(normelizedUser);
					}
				}
				
				boards.push(newBoard);
			}

			// publish:
			onBoardsReadyCB(boards);
	    };
	
		// change User Ids to Deap Ids on User Nodes:
		function normelizeUserNode(member) {
			var serviceIdField = getServiceIdField();
			// go over Person type nodes: and get users (by taskService('trello') Id) from Users services info and change id on User nodes to be the Deap Id and not service specific.
			usersAr = Users.getUsers();
			// translate serviceIds to DeapIds and assign displayName:
			for (i in usersAr){
				var user = usersAr[i];
				if(user[serviceIdField] == member.id){
			  
					member.displayName = user.displayName;
					member.id = user.id;
					return member;
				}
				
			}
	
			return null;
		}
	
		function boardsFailed(error) {
			console.log('Error, Failed to get Trello Boards for '+orgName);
	    };
	
	
		function getServiceIdField() {
			return 'trelloId'
	    };
	
		return {
			getServiceIdField:getServiceIdField,
		    getBoards: getBoards,
			getListsByBoardId:getListsByBoardId
		};
	
	})
	
	.factory('GraphBuilder', function($http,Filter,Const) {
		
		function buildUsersGraph(users){
			var graph = {	nodes:users,
							edges:[]
						}
			return graph;					
		}
		
		function buildListsGraph(boards,boardFilterOverride){
			boardFilterOverride = true;
			
			var graph = {	nodes:[],
							edges:[]
						}
							
			// go over boards
			if(boardFilterOverride || Filter.boardsIsActivated()){
				
				for (var i = 0; i < boards.length; i++) {
					
					var board = boards[i];
					
					// add boards as nodes:
					graph.nodes.push(board);
					
					for (var j = 0; j < board.lists.length; i++) {
						var list = board.lists[j];
						
						
						// TBD: implement : resourceTypeToRelationship(task['type'])
						var edge = {	srcNode:board,
										relationship: 'has' ,
										trgNode: list,
										 id:(''+(board.id)+'__'+list.id)
									}
					
						graph.edges.push(edge);
						graph.nodes.push(list);
					}
				}
			}
			return graph;
		}
		
		// TBD: if Filter jus activatd getUsers in GraphBuilder get existing model from RhiziModel service and conect tasks, lists, boards their members  which just 'arrived' 
		function buildBoardsGraph(boards,listsData,tasksData){
			var graph = {	nodes:[],
							edges:[]
						}
							
			// convert Boards:				
			graph.nodes = boards;
			
			// if Filer-users is not checked , no need to add  User edges nor User nodes:
			if(Filter.usersIsActivated()){
				memberNodesDict ={};		
				for (var i = 0; i < boards.length; i++) {
					var currentBoard = boards[i];
					for (var j = 0; j < currentBoard.members.length; j++) {	
						var member = currentBoard.members[j];
						memberNodesDict[member.id] = member;
					
						// TBD: implement : resourceTypeToRelationship(task['type'])
						var edge = {	srcNode:member,
										relationship: 'member' ,
										trgNode: currentBoard,
										 id:(''+(member.id)+'__'+currentBoard.id)
									}
					
						graph.edges.push(edge);
					}	
				}
			
				// add members to nodes list:
				// nodes: add member nodes from memberNodeDict 
				for (var property in memberNodesDict) {
				    if (memberNodesDict.hasOwnProperty(property)) {
						// collect nodes:
						graph.nodes.push(memberNodesDict[property]);
				    }
				}
			}
			
			
			
			return graph;
		}

		 return {
		   	buildBoardsGraph:buildBoardsGraph,
			buildUsersGraph:buildUsersGraph,
			buildListsGraph:buildListsGraph
		 }
	})
	// recieves graph = {nodes:[],edges:[]} and formats the graph into rhizi format:
	.factory('Formatter', function($http,Const) {

		var g_format =  {"link_id_set_rm":[],"link_set_add":[{"__dst_id":"54c566132fe34f2939cb2b28","__src_id":"54b8682712ddfc5d9565be5c","__type":["working On"],"id":"54b8682712ddfc5d9565be5c54c566132fe34f2939cb2b28"},{"__dst_id":"54c566132fe34f2939cb2b28","__src_id":"54b3ad0636d8e2eec6bf02bb","__type":["working On"],"id":"54b3ad0636d8e2eec6bf02bb54c566132fe34f2939cb2b28"}],"node_id_set_rm":[],"node_set_add":[{"__label_set":["skill"],"avgFeedback":null,"description":null,"enddate":"","feedback":null,"id":"54d8692e0774266e79fee223","name":"Refactor code","startdate":"","type":"skill","url":"https://trello.com/c/KGfhD9Uv/9-refactor-code"},{"__label_set":["Person"],"avgFeedback":null,"description":null,"enddate":"","feedback":null,"id":"54b8682712ddfc5d9565be5c","name":"shaharhalutz","startdate":"","type":"person","url":"https://trello.com/shaharhalutz"},{"__label_set":["skill"],"avgFeedback":null,"description":null,"enddate":"","feedback":null,"id":"54c566132fe34f2939cb2b28","name":"Platform meeting 27-1-2015","startdate":"","type":"skill","url":"https://trello.com/c/rU6iaCZT/1-platform-meeting-27-1-2015"},{"__label_set":["Person"],"avgFeedback":null,"description":null,"enddate":"","feedback":null,"id":"54b3ad0636d8e2eec6bf02bb","name":"talserphos","startdate":"","type":"person","url":"https://trello.com/talserphos"}]}
		
		function format(grph) {
			var g_format = {link_id_set_rm:[],link_set_add:[],node_id_set_rm:[],node_set_add:[]}
			//var link_set_format = {"__dst_id":"","__src_id":"","__type":[],"id":""}
			//var node_set_format = {"__label_set":[],"description":"","enddate":"","id":"","name":"","startdate":"","type":"skill","url":""}

			// prepare links:
			var relations = grph.edges;
			var nodesDict = {};

			// go over sole nodes:
			var nodes = grph.nodes;
			for (var i = 0; i < nodes.length; i++) {
				var node = nodes[i];

				var nodeLabels = [node.base];
				var nodeLabels = [node.type];
				var node_set_format = {__label_set:nodeLabels,
									description:node.description,
									enddate:"",
									id:node.id,
									name:node.displayName,
									startdate:"",
									type:node.type,
									url:node.url,
									feedback:node.feedback,
									avgFeedback:node.avgFeedback
									};

				g_format.node_set_add.push(node_set_format)
			}
			// go over relations:
			for (var i = 0; i < relations.length; i++) {

				var relation = relations[i];
				
				// prepare nodes dictionary and write on top of same node (dont hold duplicates - by id):
				nodesDict[relation.srcNode.id] = relation.srcNode;
				nodesDict[relation.trgNode.id] = relation.trgNode

				var link_set_format = {	__dst_id:relation.trgNode.id,
										__src_id:relation.srcNode.id,
										__type:[relation.relationship],
										id:relation.id}
				g_format.link_set_add.push(link_set_format);
			}

			return g_format;
		};

	  return {
		format:format,
	    compileGformat: function(data) {
	      return g_format;
	    }
	  };
	
	})


	// 	Aggregator API:
	//  	getData:  calls onReady cb, each time  we have some graph data (node and links) ready for publishing.
	//			params: 
	//				onReadyCB, callback
	
	.factory('Aggregator', function(Tasks,Filter,Users,Feedback,Formatter,GraphBuilder) {
		
		var onDataReadyCB;
		
		function getNodesFeedback(graphData) {
			return true;
		}
		
		function onTasksDataError(error) {
			console.log('onTasksDataError: '+error);
		};
		
		// TBD: generelize Data Model, add type' field inorder , to be able to do : onGetDataSuccess
		function onBoardsSuccess(boards) {
			console.log('onBoardsSuccess: boards:');
			console.dir(boards);

			// build graph:
			boardsGraphData = GraphBuilder.buildBoardsGraph(boards,null,null);
			
			// fill in Feedback on all nodes 
			// TBD: change feedback implementation to be on click on tooltip - load specific myfeedbaclk form, and if activated feedback filter: load all Avg feedbacks, and update graph
		 	
			//if(Filter.feedbackIsActivated){
				getNodesFeedback(boardsGraphData);	
			//}
			
			publishGraphData(boardsGraphData);
		};
		

		
		
		function publishGraphData(graphData) {
			console.log('Aggregator:publishGraphData : completed cycle - graphData:');
			console.dir(graphData);
			
			var payload = Formatter.format(graphData);
			
			if(onDataReadyCB){
				onDataReadyCB(payload);
			}
			else{
				console.log('publishGraphData: onDataReadyCB, is undefined.');
			}
		};
		
		function getData(onReadyCB,query) {
			onDataReadyCB = onReadyCB;
			
			// TBD: execute actions according to Filter:
			
			// get Boards:
			Tasks.getBoards(onBoardsSuccess,onTasksDataError);
	    
			return true;
	    };
	
		function getBoards(onReadyCB,query) {
			onDataReadyCB = onReadyCB;
			
			// get Boards:
			Tasks.getBoards(onBoardsSuccess,onTasksDataError);
	    
			return true;
	    };
	
		function removeBoards(onReadyCB,query) {
			onDataReadyCB = onReadyCB;
			console.log('removeBoards:');

			return true;
	    };
	
		function getUsers(onReadyCB,query) {
			console.log('Aggregator: getUsers');
			onDataReadyCB = onReadyCB;
			
			// TBD: if Filter just activatd getUsers in GraphBuilder get existing model from RhiziModel service and conect tasks, lists, boards their members  which just 'arrived' 
			// but temporarily we aslo get boards
			// get Boards:
			//Tasks.getBoards(onBoardsSuccess,onTasksDataError);
		
			// get Users:
			var users = Users.getUsers();
			
			// build graph:
			var usersGraphData = GraphBuilder.buildUsersGraph(users);

			// fill in Feedback on all nodes 
			// TBD: change feedback implementation to be on click on tooltip - load specific myfeedbaclk form, and if activated feedback filter: load all Avg feedbacks, and update graph

			//if(Filter.feedbackIsActivated){
				getNodesFeedback(usersGraphData);	
			//}

			publishGraphData(usersGraphData);
			
			// check Filter if need to load Boards (no need to load model from rhizi - since we need to know whichboards go where):
			if(Filter.boardsIsActivated()){
				getBoards(onReadyCB);
			}
			

			return true;
	    };
	
		function removeUsers(onReadyCB,query) {
			onDataReadyCB = onReadyCB;
			console.log('removeUsers:');
			
	
			return true;
	    };
		
		
		
		
		function getListsByBoard(onReadyCB,boardId) {
			onDataReadyCB = onReadyCB;
			console.log('getListsByBoard:');
			
			Tasks.getListsByBoardId(onListsSuccess,onTasksDataError,boardId);
			
	
			return true;
	    };
		
		// TBD: generelize Data Model, add type' field inorder , to be able to do : onGetDataSuccess
		function onListsSuccess(boards) {
			console.log('onListsSuccess: boards:');
			console.dir(boards);

			// build graph:
			boardsGraphData = GraphBuilder.buildListsGraph(boards);
			
			// fill in Feedback on all nodes 
			// TBD: change feedback implementation to be on click on tooltip - load specific myfeedbaclk form, and if activated feedback filter: load all Avg feedbacks, and update graph
		 	
			//if(Filter.feedbackIsActivated){
				getNodesFeedback(boardsGraphData);	
			//}
			
			publishGraphData(boardsGraphData);
		};
		
		return {
		  removeUsers:removeUsers,
	  	  getUsers:getUsers,
		  removeBoards:removeBoards,
  		  getBoards:getBoards,
		  getListsByBoard:getListsByBoard,
		  getData: getData
		};
	
	});

