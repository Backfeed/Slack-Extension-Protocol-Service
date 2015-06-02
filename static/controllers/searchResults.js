angular.module('MyApp')
  .controller('SearchResultsCtrl', function($scope,$auth,$location,Filter,Const,Aggregator,Account) {
		
		// get account so we have trello token:
		Account.getProfile()
	        .success(function(data) {
				console.log('profileData:');
				console.dir(data);
				Account.setUserData(data);

	        })
	        .error(function(error) {
	          $alert({
	            content: error.message,
	            animation: 'fadeZoomFadeDown',
	            type: 'material',
	            duration: 3
	          });
	        });
		
		
		// TBD: move Constantsto Const service after changing css definition (colors etc) in rhizi with our naming
		var NODE_TYPE_BOARDS = 'Boards';
		var NODE_TYPE_LISTS = 'Lists';
		var NODE_TYPE_TASKS = 'Tasks';
		var NODE_TYPE_USERS = 'Users';
		
		$scope.filterData  = Filter.getData();



		// if not authenticated return to splash:
		if(!$auth.isAuthenticated()){
			$location.path('splash'); 
	    }
	
		console.log("listening to NodeClicked events.")
		
		// Connect search Page as a Delegate to Rhizi UI:
		
		window.addEventListener("message", function(event) {
			console.log("recieved message from Rhizi:");
			
		    // We only accept messages from ourselves
		    if (event.source != window){
				console.log("event source is note window - exiting.")
		      	return;
			}
			
			// check Rhizi origin events:
			if (!event.data.type) {
				console.log("event type is undefined - exiting.")
		      	return;
			}
			
			// Sanity:
			if( !event.data.node){
				console.log("event data node is undefined - exiting.")
		      	return;
			}
			
			switch(event.data.type) {
			    case "FeedbackNodeClicked":
					$scope.feedbackNodeClicked(event.data.node);
			        break;
			
			    case "ExpandNodeClicked":
					$scope.expandNodeClicked(event.data.node);
			        break;
			    
				default:
			        console.log('event type unknown.');
			}
			
		}, false);
		
		// Rhizi delegate protocol :
		$scope.feedbackNodeClicked = function(node){
			console.log("feedbackNodeClicked, recieved from Rhizi UI. node:");
			console.dir(node);
		}
		
		$scope.expandNodeClicked = function(node){
			console.log("expandNodeClicked, recieved from Rhizi UI. node:");
			console.dir(node);
			
			if(node.type == 'skill'){
				//Aggregator.getListsByBoard($scope.pushToRhizi,node.id);
			}
			if(node.type == 'person'){
				//Aggregator.getBoards($scope.pushToRhizi);
			}
		}
		
		$scope.pushToRhizi = function(input){
			console.log('pushing to rhizi:');
			console.dir(input);

			// Rhizi push API:  TBD: assign a rhizi object (not global window)
			window.push(input);
		}
		
		
		// Filter:
		$scope.filterClick = function(filter){
			var stateBeforeToggle = filter.selected;
			
			filter.selected = !filter.selected;
			Filter.setData($scope.filterData);
			
			// TBD: give  search query as parameter?
	        
			// activae aggregator API:
			switch(filter.type) {
			    case NODE_TYPE_BOARDS:
			
					if(filter.selected){
						Aggregator.getBoards($scope.pushToRhizi);
				    }
					else{
						//Aggregator.removeBoards($scope.pushToRhizi);
						// TBD: temporary solution till implemented removeUsers:
						window.reset();
						if(Filter.usersIsActivated()){
							Aggregator.getUsers($scope.pushToRhizi);
						}
					}
					
			        break;
			
			    case NODE_TYPE_USERS:
					if(filter.selected){
				        Aggregator.getUsers($scope.pushToRhizi);
				    }
					else{
						//Aggregator.removeUsers($scope.pushToRhizi);
						// TBD: temporary solution till implemented removeUsers:
						window.reset();
						if(Filter.boardsIsActivated()){
							Aggregator.getBoards($scope.pushToRhizi);
						}
					}
			
			        break;
			    default:
			        console.log('filter unknown.');
			}

		}
  	});