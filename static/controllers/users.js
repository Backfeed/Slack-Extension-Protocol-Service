angular.module('MyApp')
  .controller('UsersCtrl', function($scope,$auth,$location,Users) {
	
	// if not authenticated return to splash:
	if(!$auth.isAuthenticated()){
		$location.path('splash'); 
    }

	$scope.users = Users.getUsers();
	
	console.log('$scope.users:')
	console.dir($scope.users)
	
	//$scope.users = User.query();
  	$scope.orderProp = "targetName"; // set initial order criteria
	
});