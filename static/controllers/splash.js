angular.module('MyApp')
  .controller('SplashCtrl', function($scope, $alert, $auth,$location) {
		var body = document.getElementsByTagName('body')[0];
		var element = angular.element(body);
		element.addClass('splash-background')
    $scope.changeView = function(view){
        $location.path(view); // path not hash

		// remove splash:
		var body = document.getElementsByTagName('body')[0];
		var element = angular.element(body);
		element.removeClass('splash-background')
	 }
	
	$scope.authenticate = function(provider) {
      $auth.authenticate(provider)
        .then(function() {
          $alert({
            content: 'You have successfully logged in',
            animation: 'fadeZoomFadeDown',
            type: 'material',
            duration: 3
          });
		  $scope.changeView('search')
			
        })
        .catch(function(response) {
          $alert({
            content: response.data ? response.data.message : response,
            animation: 'fadeZoomFadeDown',
            type: 'material',
            duration: 3
          });
        });
    };
	/*
	if ($auth.isAuthenticated()){
		
		$scope.changeView('profile')
	}
*/
	// view background only in splash view
    $scope.isActive = function(route) {
        return route === $location.path();
    }


  });













