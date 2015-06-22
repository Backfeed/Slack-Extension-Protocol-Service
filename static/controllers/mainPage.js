angular.module('MyApp').controller(
		'MainPageCtrl',
		function($scope, $auth, $location, $stateParams, $alert, Contributions,
				ContributionDetail, SaveContribution, CloseContribution,
				Account, Users,CTagKey,ngProgress) {			
			var orgExists;
			$scope.organizationId = 'notintialized';
			$scope.buttonDisabled = true;
			$scope.model = {
				title : '',
				file : '',
				owner : '',
				min_reputation_to_close : '',
				users_organizations_id : '',
				contributers : [ {
					contributer_id : '0',
					contributer_percentage : '',
					contribution1: '50',
					img:'images/avatar.jpg'
				} ],
				intialBid : [ {
					tokens : '',
					reputation : ''
				} ]

			}
			
				$scope.cTagKey =  CTagKey;
			    $scope.mainQuery = '';
				$scope.cTags = [];
				

			    $scope.createTagClicked = function(tag) {

						$scope.cTagKey.addCTag(tag);
				};

				$scope.removeTagClicked = function(tag) {

						$scope.cTagKey.removeCTag(tag);
				};

				$scope.userUpdatedQuery = function() {
						$scope.cTagKey.analyzeQuery($scope.cTagKey.query);
				};

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

					}
				};

				$scope.updateValue = function (text,value) {
			        alert(text+': ' + value);
			    };
			
			// if not authenticated return to splash:
			if (!$auth.isAuthenticated()) {
				$location.path('splash');
			} else {
				$scope.getProfile = function() {
					Account.getProfile().success(function(data) {
						$scope.userId = data.userId;						
						orgExists = data.orgexists;
						if (orgExists == 'true') {
							$scope.users_organizations_id = data.userOrgId;
							$scope.model.users_organizations_id = data.userOrgId;
							$scope.organizationId = data.orgId;
							$scope.access_token = data.access_token;
						}
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

				$scope.ifOrgExists = function() {
					if (Account.getUserData() != undefined) {
						$scope.user = Account.getUserData();						
						if (Account.getUserData().orgexists == 'false') {
							orgExists = "false";
							return false;
						} else {
							orgExists = "true";
							return true;
						}
					} 

				};

				userData = Account.getUserData();
				if (userData == undefined) {
					$scope.getProfile();
				} else {
					$scope.userId = userData.userId;
					orgExists = userData.orgexists;
					if (orgExists == 'true') {
						$scope.users_organizations_id = userData.userOrgId;
						$scope.organizationId = userData.orgId;
						$scope.model.users_organizations_id = userData.userOrgId;
					}
					$scope.model.owner = userData.userId;
				}
				

				if ($auth.isAuthenticated()) {
					$scope.contributions = Contributions.getAllContributions({
						organizationId : $scope.organizationId
					});
				}

			}

		});
