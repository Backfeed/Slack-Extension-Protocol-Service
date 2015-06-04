angular.module('MyApp')
  .controller('ContributionsCtrl', function($scope,$auth,$location,$stateParams,Contributions,ContributionDetail,SaveContribution,CloseContribution) {
	  $scope.contributionId = $stateParams.contributionId;
	
	// if not authenticated return to splash:
	if(!$auth.isAuthenticated()){
		$location.path('splash'); 
    }


	//$scope.slackUsers = Users.getUsers();
  $scope.ContributionModel = {			
			file : '',
			owner : '',
			min_reputation_to_close : '',
			contributers : [{contributer_id:'',contributer_percentage:''}],
			intialBid : [{tokens:'',reputation:''}]	
	};  
  
  $scope.ContributionModelForView = {			
			file : '',
			owner : '',
			min_reputation_to_close : '',
			contributionContributers : [{contributer_id:'',contributer_percentage:''}],
			bids : [{tokens:'',reputation:''}]	
	};
  
  $scope.removeContributionItem = function(index) {
      $scope.ContributionModel.contributers.splice(index, 1);
};
   $scope.getContribution = function(entity) {
		var constributionId = 0;
		if(entity){
			contributionId = entity.id;
		}
		console.log("get Contribution "+contributionId);
		$location.path("/contribution/"+ contributionId);
			
	};
	
	$scope.createContribution = function(){
		console.log("Create Contribution");		
		console.log($scope.ContributionModel);
		$location.path("/contribution");
	};
	$scope.addBid = function(){
		console.log("Create Bid");		
		console.log($scope.ContributionModelForView.id);
		$location.path("/bids/"+$scope.ContributionModelForView.id);
	};
	$scope.contributions = Contributions.getAllContributions();

	if($scope.contributionId && $scope.contributionId != 0){
		$scope.data1 = ContributionDetail.getDetail({contributionId:$scope.contributionId});	
		$scope.data1.$promise.then(function (result) {
				$scope.ContributionModelForView = result;				
			});	
	}
	$scope.addContributer = function() {
		$scope.ContributionModel.contributers.push({
			contributer_id:'',
			contributer_percentage:''
		}) ;
	};
	
	//$scope.users = User.query();
  	$scope.orderProp = "targetName"; // set initial order criteria
	$scope.submit = function(){
		console.log("In Submit method");
		console.log($scope.ContributionModel)
		$scope.data = SaveContribution.save({},$scope.ContributionModel);
		$scope.data.$promise.then(function (result) {
			alert('Successfully saved');
			$location.path("/contributions");
		});
	};
	
	$scope.closeContribution = function(){
		console.log("In closeContribution method");
		console.log($scope.ContributionModelForView.id)
		$scope.data = CloseContribution.save({},$scope.ContributionModelForView);
		$scope.data.$promise.then(function (result) {
			alert('Contribution closed');
			$location.path("/contributions");
		});
		
	};
	
});