angular.module('MyApp').controller('NavbarCtrl',
		function($scope, $auth, Account, $alert, $location,OrgDelete) {

			$scope.createOrg = function() {
				console.log("Create Org");
				$location.path("/organization");
			};

			$scope.isAuthenticated = function() {
				return $auth.isAuthenticated();
			};
			$scope.ifOrgExists = function() {
				if (Account.getUserData() != undefined) {					
					$scope.user = Account.getUserData();
					console.log(Account.getUserData().orgexists)
					if (Account.getUserData().orgexists == 'false') {
						return false;
					} else {
						return true;
					}
				}

			};
			
			$scope.deleteOrg = function() {
				if (Account.getUserData() != undefined) {					
					$scope.user = Account.getUserData();
					console.log(Account.getUserData().orgexists)
					if (Account.getUserData().orgexists == 'false') {
						return false;
					} else {
						organizationId = Account.getUserData().orgId;
						var r = confirm("Are you confirm you want to delete organization. If yes then it will delete all users,contributions and bids under this org :"+organizationId);
						var txt = '';
						if (r == true) {
							$scope.data = OrgDelete.delete({
								OrgId : organizationId
							});
							$scope.data.$promise.then(function(result) {
								alert('Organization deleted');
								$location.path("/logout");
							});
						} 
					}
				}

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
		});