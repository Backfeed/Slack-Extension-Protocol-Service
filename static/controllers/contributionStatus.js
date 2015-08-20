angular.module('MyApp').controller(
		'ContributionStatusCtrl',
		function($scope, $auth, $location, $stateParams, $alert, ContributionStatus,				
				Account, Users) {			
			$scope.cotributionStatusModel = {
					file:'',
					title:'',
					currentValuation : '',
					myWeight : '',
					myValuation : '',
					reputationDelta : '',
					groupWeight : '',
					bids : [ {
						time_created : '',
		                tokens:'',
		                reputation: '',
		                contribution_value_after_bid:''
		            } ]
				};
			$scope.getContributionStatus = function(){
	        	if ($scope.contributionId && $scope.contributionId != 0 && $scope.userId && $scope.userId != 0) {
					$scope.contributionStatus = ContributionStatus.getDetail({
						id : $scope.contributionId,userId : $scope.userId
					});
					$scope.contributionStatus.$promise.then(function(result) {
						$scope.cotributionStatusModel = result;
					});
	        	}
	        };
			// if not authenticated return to splash:
			if (!$auth.isAuthenticated()) {
				$location.path('splash');
			} else {
														
				$scope.contributionId = $stateParams.contributionId;
				$scope.getProfile = function() {
					Account.getProfile().success(function(data) {
						$scope.userId = data.userId;
						Account.setUserData(data);
						$scope.getContributionStatus();

					}).error(function(error) {
						$alert({
							content : error.message,
							animation : 'fadeZoomFadeDown',
							type : 'material',
							duration : 3
						});
					});
				};
				userData = Account.getUserData();
				console.log("userData is" + userData);
				if (userData == undefined) {
					$scope.getProfile();
				} else {
					$scope.userId = userData.userId;
					$scope.getContributionStatus();
				}
				if ($scope.contributionId && $scope.contributionId != 0 && $scope.userId && $scope.userId != 0) {
					$scope.data1 = ContributionStatus.getDetail({
						id : $scope.contributionId,userId : $scope.userId
					});
					$scope.data1.$promise.then(function(result) {
						$scope.cotributionStatusModel = result;
					});
				}
				

			}

		});
