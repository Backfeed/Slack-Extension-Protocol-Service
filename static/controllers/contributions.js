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
  $scope.BidModel = {			
		    tokens : '',
			owner : '',
			reputation : '',
			contribution_id : ''
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
		console.log($scope.ContributionModelForView);
		$scope.BidModel.contribution_id = $scope.ContributionModelForView.id
		$location.path("/bids");
	};
	$scope.contributions = Contributions.getAllContributions();
	$scope.gridQueryOptions = { 
	        data: 'myData',
	        columnDefs: [
	                     {field:'id', displayName:'ID',visible:false},
	                     {field:'file', displayName:'File',cellTemplate:'<a style="cursor:pointer" ng-click="getQuery(row.entity)">{{row.getProperty("file")}} </span></div>'}, 
	                     {field:'status', displayName:'Status',cellTemplate:'<div class="ngCellText"><a title="{{row.entity.status}}"  style="text-decoration:none;color:#000000">{{row.getProperty("status")}}</a></div>'}
	                     ]
	    };

	if($scope.contributionId && $scope.contributionId != 0){
		$scope.data1 = ContributionDetail.getDetail({contributionId:$scope.contributionId});	
		$scope.data1.$promise.then(function (result) {
				$scope.ContributionModelForView = result;
				console.log("This is "+$scope.ContributionModelForView);
				console.log("Status is "+$scope.ContributionModelForView.status);
				console.log("Id is "+$scope.ContributionModelForView.status);
				console.log("File is "+$scope.ContributionModelForView.file);
				
			});	
	}
	$scope.addContributer = function() {
		$scope.ContributionModel.contributers.push({
			contributer_id:'',
			contributer_percentage:''
		}) ;
	};
	console.log('$scope.contributions:')
	console.log($scope.contributions)
	
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