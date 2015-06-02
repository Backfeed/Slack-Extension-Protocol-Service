angular.module('MyApp')
  .controller('NavbarCtrl', function($scope, $auth,Account,$alert,$location,Query,Aggregator) {
    $scope.isAuthenticated = function() {
      return $auth.isAuthenticated();
    };
	
	$scope.getProfile = function() {
      Account.getProfile()
        .success(function(data) {
          $scope.user = data;
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

	$scope.user = {displayName:"profile"};
	if( $auth.isAuthenticated()){
		$scope.getProfile()
	}

	// Search:
	$scope.query = '';
	
	$scope.searchButtonClicked = function (event){
		console.log('angular: searchButtonClicked - navigating to searchPage.');
		$location.path('search');
		
		
		// push API:
		
		Aggregator.getData( function(input) {
			console.log('pushing to rhizi:');
			console.dir(input);
			
			window.reset();
		});
	
	}

  });