angular.module('MyApp')
  .controller('BidsCtrl', function($scope,$auth,$location,$stateParams,Users,SaveBidTOContribution) {
	  $scope.contributionId = $stateParams.contributionId;
	  $scope.bidId = $stateParams.bidId;
	// if not authenticated return to splash:
	if(!$auth.isAuthenticated()){
		$location.path('splash'); 
    }

	//$scope.slackUsers = Users.getUsers();
 
  $scope.BidModel = {			
		    tokens : '',
			owner : '',
			reputation : '',
			contribution_id : ''
	};
  
	
	

	if($scope.contributionId && $scope.contributionId != 0){
		 $scope.BidModel.contribution_id = $scope.contributionId ;
	}
	
	
	//$scope.users = User.query();
  	$scope.orderProp = "targetName"; // set initial order criteria
	$scope.submit = function(){
		console.log("In Submit method");
		console.log($scope.BidModel)
		$scope.data = SaveBidTOContribution.save({},$scope.BidModel);
		$scope.data.$promise.then(function (result) {
			alert('Successfully saved');
			$location.path("/contribution/"+$scope.contributionId);
		});
		
	};
	
	
});