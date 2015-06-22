angular.module('MyApp').controller(
		'ResultsCtrl',
		function($scope, $auth, $location, $stateParams, $alert, Contributions,
				ContributionDetail, SaveContribution, CloseContribution,
				Account, Users,CTagKey,ngProgress) {

	$scope.links = [{name:'link1'},{name:'link2'},{name:'link3'}];

	$scope.cTagKey =  CTagKey;
    $scope.query = '';
	$scope.cTags = [];

	
	$scope.$watch(function () {
		       return CTagKey.cTags;
		     },                       
		      function(newVal, oldVal) {
				$scope.cTags = CTagKey.cTags;
				if(newVal && ($scope.cTagKey.query != '')){
					 //$scope.userUpdatedQuery();

				}
		      	else{
					//$scope.query = '';
				}
	}, true);
	
	$scope.isAuthenticated = function() {
		return $auth.isAuthenticated();
	};
	
	$scope.getProfile = function() {
		Account.getProfile().success(function(data) {
			$scope.user = data;
			Account.setUserData(data);
		}).error(function(error) {
			$alert({
				content : error.message,
				animation : 'fadeZoomFadeDown',
				type : 'material',
				duration : 3
			});
		});
	};

	$scope.user = {
		displayName : "profile"
	};
	if ($auth.isAuthenticated() == true) {
		if (Account.getUserData() == undefined) {
			$scope.getProfile()
		}

	}

	$scope.createTagClicked = function(tag) {

			$scope.cTagKey.addCTag(tag);
	};

	$scope.removeTagClicked = function(tag) {

			$scope.cTagKey.removeCTag(tag);
	};
	$scope.userUpdatedQuery = function() {
			$scope.cTagKey.analyzeQuery($scope.cTagKey.query);
	};

    $scope.searchButtonClicked = function() {
	//	alert('searching for:'+$scope.query);
	};

	$scope.getClass =  function (){
		if($scope.isIndexPage()){
			return 'my-navbar';
		}
		return '' ;
	}

	$scope.isIndexPage =  function (){
		if( $location.path()=='/mainPage' || 
			$location.path()==''){

			return true;
		}
		return false;
	}

	$scope.inputIsValid = function() {
		if($scope.cTagKey.cTags.length){
			return true;
		}
		return false;
	};

    $scope.searchButtonClicked = function(event) {

		// TBD: prepare robust input validation
		if($scope.inputIsValid()){
			ngProgress.color('blue');
			ngProgress.start();
			setTimeout(function() {ngProgress.complete();	$location.path( '/results' ); 	$scope.$apply();}, 3000);
		}
		else{
			alert('You must enter at least 1 ChaTag.');
			//MessageUser.messageUser('You must enter at least 1 ChaTag.');

		}
	};




});