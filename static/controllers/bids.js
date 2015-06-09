angular.module('MyApp')
  .controller('BidsCtrl', function($scope,$auth,$location,$stateParams,Users,$alert,SaveBidTOContribution,Account) {
	  $scope.contributionId = $stateParams.contributionId;
	  $scope.bidId = $stateParams.bidId;
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
	    $scope.bid = {			
			    tokens : '',
				owner : '',
				reputation : '5',
				contribution_id : ''
		};
	  
	     userData = Account.getUserData();
		 console.log("userData is"+userData);
		 if(userData == undefined){
			 $scope.getProfile();
		 }else{
			 $scope.bid.owner = userData.userId;
		 }
	// if not authenticated return to splash:
	if(!$auth.isAuthenticated()){
		$location.path('splash'); 
    }

	//$scope.slackUsers = Users.getUsers();
  
   
	
                     
              

	if($scope.contributionId && $scope.contributionId != 0){
		$scope.bid.contribution_id =$scope.contributionId ;
	}
	
	
	//$scope.users = User.query();
	$scope.orderProp = "targetName"; // set initial order criteria
	$scope.submit = function(){
		console.log("In Submit method");
		console.log($scope.bid)
		$scope.data = SaveBidTOContribution.save({},$scope.bid);
		$scope.data.$promise.then(function (result) {
			alert('Bid Successfully created');
			$location.path("/contribution/"+$scope.contributionId);
		});
		
	};
	
	
});