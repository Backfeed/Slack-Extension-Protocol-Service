angular.module('MyApp')
  .controller('BidsCtrl', function($scope,$auth,$location,$stateParams,Users,$alert,SaveBidTOContribution,Account) {
	  var vm = this;
	  vm.contributionId = $stateParams.contributionId;
	  vm.bidId = $stateParams.bidId;
	  $scope.getProfile = function() {
	      Account.getProfile()
	        .success(function(data) {
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
	    };
	    vm.bid = {			
			    tokens : '',
				owner : '',
				reputation : '',
				contribution_id : ''
		};
	  
	     userData = Account.getUserData();
		 console.log("userData is"+userData);
		 if(userData == undefined){
			 $scope.getProfile();
		 }else{
			 vm.bid.owner = userData.userId;
		 }
	// if not authenticated return to splash:
	if(!$auth.isAuthenticated()){
		$location.path('splash'); 
    }

	//$scope.slackUsers = Users.getUsers();
  
   
	
   vm.bidFields = [
                      {
                          key: 'tokens',
                          type: 'input',
                          templateOptions: {
                              type: 'text',
                              label: 'Tokens',
                              placeholder: 'Enter Tokens',
                              required: true
                          }
                      },
                      {
                          key: 'reputation',
                          type: 'input',
                          templateOptions: {
                              type: 'text',
                              label: 'Reputation',
                              placeholder: 'Enter Reputation',
                              required: true
                          }
                      }
                  ];
                  
              

	if(vm.contributionId && vm.contributionId != 0){
		 vm.bid.contribution_id =vm.contributionId ;
	}
	
	
	//$scope.users = User.query();
	vm.orderProp = "targetName"; // set initial order criteria
	vm.submit = function(){
		console.log("In Submit method");
		console.log(vm.bid)
		vm.data = SaveBidTOContribution.save({},vm.bid);
		vm.data.$promise.then(function (result) {
			alert('Bid Successfully created');
			$location.path("/contribution/"+vm.contributionId);
		});
		
	};
	
	
});