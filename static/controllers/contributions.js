angular.module('MyApp')
  .controller('ContributionsCtrl', function($scope,$auth,$location) {
	
	// if not authenticated return to splash:
	if(!$auth.isAuthenticated()){
		$location.path('splash'); 
    }

	//$scope.slackUsers = Users.getUsers();

	
	$scope.contributions = [{
						realName:'shahar halutz',
						email:'myemail',
						rep:'90',
						activated:true,
						avatar:"https:\/\/secure.gravatar.com\/avatar\/03fd4d2ade5296050301cf22ef3c639c.jpg"
					},
					{
						realName:'yosi ofi',
						email:'myemail2',
						rep:'30',
						activated:false,
						avatar:"https:\/\/secure.gravatar.com\/avatar\/03fd4d2ade5296050301cf22ef3c639c.jpg"
					},
					{
						realName:'schelich levo',
						email:'myemail3',
						rep:'40',
						activated:true,
						avatar:"https:\/\/secure.gravatar.com\/avatar\/03fd4d2ade5296050301cf22ef3c639c.jpg"
					}
	]
	
	console.log('$scope.contributions:')
	console.dir($scope.contributions)
	
	//$scope.users = User.query();
  	$scope.orderProp = "targetName"; // set initial order criteria
	
});