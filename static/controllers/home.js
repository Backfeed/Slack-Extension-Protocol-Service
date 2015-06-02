angular.module('MyApp')
  .controller('HomeCtrl', function($scope,$auth,$location) {
	
	// if not authenticated return to splash:
	if(!$auth.isAuthenticated()){
		$location.path('splash'); 
    }
	
});