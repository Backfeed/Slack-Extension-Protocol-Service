angular.module('MyApp')
  .controller('ContributionsCtrl', function($scope,$auth,$location,Users,Contributions,ContributionDetail,SaveContribution) {
	
	// if not authenticated return to splash:
	//if(!$auth.isAuthenticated()){
	//	$location.path('splash'); 
    //}

	//$scope.slackUsers = Users.getUsers();
  $scope.ContributionModel = {			
			file : '',
			owner : '',
			min_reputation_to_close : '',
			contributers : [{contributer_id:'',contributer_percentage:''}],
			intialBid : [{tokens:'',reputation:''}]	
	};
  $scope.testModel = {			
			file : '',
			id : '',
			status : ''						
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
		test1 = ContributionDetail.getDetail({contributionId:entity.id});
		console.log("This is print"+ JSON.stringify(test1));
		console.log("This is print"+ JSON.stringify(test1).file);		
		//console.log("query id is : " + queryId);
		$location.path("/contribution/"+ contributionId);
	};
	$scope.createContribution = function(){
		console.log("Create Contribution");		
		console.log($scope.ContributionModel);
		$location.path("/contribution");
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

	if($scope.id && $scope.id != 0){
		$scope.ContributionModel = ContributionDetail.getDetail({contributionId:$scope.id});
		console.log($scope.ContributionModel);
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
	
});