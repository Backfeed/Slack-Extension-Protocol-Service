angular.module('MyApp')
  .controller('NavbarCtrl', function($scope, $auth,Account,$alert,$location) {
    $scope.isAuthenticated = function() {
      return $auth.isAuthenticated();
    };
	
	$scope.getProfile = function() {
      Account.getProfile()
        .success(function(data) {        	
          $scope.user = data;
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

	$scope.user = {displayName:"profile"};
	if( $auth.isAuthenticated()){
		$scope.getProfile()
	}
  });