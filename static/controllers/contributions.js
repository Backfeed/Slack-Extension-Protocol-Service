angular.module('MyApp').controller(
		'ContributionsCtrl',
		function($scope, $auth, $location, $stateParams, $alert, Contributions,
				ContributionDetail, SaveContribution, CloseContribution,
				Account, Users) {
			var vm = this;
			var orgExists;
			$scope.organizationId = 'notintialized';
			vm.model = {
				title : '',
				file : '',
				owner : '',
				min_reputation_to_close : '',
				users_organizations_id : '',
				contributers : [ {
					contributer_id : '',
					contributer_percentage : ''
				} ],
				intialBid : [ {
					tokens : '',
					reputation : ''
				} ]

			}
			// if not authenticated return to splash:
			if (!$auth.isAuthenticated()) {
				$location.path('splash');
			} else {
				vm.getProfile = function() {
					Account.getProfile().success(function(data) {
						$scope.userId = data.userId;
						vm.userId = data.userId;
						orgExists = data.orgexists;
						if (orgExists == 'true') {
							$scope.users_organizations_id = data.userOrgId;
							vm.model.users_organizations_id = data.userOrgId;
							$scope.organizationId = data.orgId;
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
					vm.getProfile();
				} else {
					vm.userId = userData.userId;
					orgExists = userData.orgexists;
					if (orgExists == 'true') {
						$scope.users_organizations_id = userData.userOrgId;
						$scope.organizationId = userData.orgId;
						vm.model.users_organizations_id = userData.userOrgId;
					}
					vm.model.owner = userData.userId;
				}

				vm.getOrgUsers = function() {
					$scope.data = Users.getOrg.getUsers({
						organizationId : $scope.organizationId
					});
					$scope.data.$promise.then(function(result) {
						Users.setAllOrgUsersData(result)						
						vm.users = result;
						init();
						//$location.path("/contribution/" + result.id);
					});
				};

				allOrgUsersData = Users.getAllOrgUsersData();
				if (orgExists == 'true') {
					if (allOrgUsersData == undefined) {
						vm.getOrgUsers();
					} else {

						vm.users = allOrgUsersData;
						init();
					}
				}

				vm.contributionId = $stateParams.contributionId;

				vm.ContributionModelForView = {
					title : '',
					file : '',
					owner : '',
					min_reputation_to_close : '',
					users_organizations_id : '',
					contributionContributers : [ {
						contributer_id : '',
						contributer_percentage : ''
					} ],
					bids : [ {
						tokens : '',
						reputation : ''
					} ]
				};

				$scope.getContribution = function(entity) {
					var constributionId = 0;
					if (entity) {
						contributionId = entity.id;
					}
					console.log("get Contribution " + contributionId);
					$location.path("/contribution/" + contributionId);

				};

				vm.originalFields = angular.copy(vm.fields);
				// function definition
				vm.onSubmit = function() {
					console.log("In Submit method");
					console.log(vm.model)
					$scope.data = SaveContribution.save({}, vm.model);
					$scope.data.$promise.then(function(result) {
						alert('Successfully saved');
						$location.path("/contribution/" + result.id);
					});
				};
				$scope.createContribution = function() {
					console.log("Create Contribution");
					console.log(vm.model);
					$location.path("/contribution");
				};
				$scope.addBid = function() {
					console.log("Create Bid");
					console.log($scope.ContributionModelForView.id);
					$location.path("/bids/"
							+ $scope.ContributionModelForView.id);
				};
				$scope.showStatus = function() {
					console.log("Show Status");
					console.log($scope.ContributionModelForView.id);
					$location.path("/contributionStatus/"
							+ $scope.ContributionModelForView.id);
				};
				

				if (vm.contributionId && vm.contributionId != 0) {
					$scope.data1 = ContributionDetail.getDetail({
						contributionId : vm.contributionId
					});
					$scope.data1.$promise.then(function(result) {
						$scope.ContributionModelForView = result;
					});
				}
				//$scope.users = User.query();
				$scope.orderProp = "time_created"; // set initial order criteria

				$scope.closeContribution = function() {
					console.log("In closeContribution method");
					console.log($scope.ContributionModelForView.id)
					$scope.data = CloseContribution.save({},
							$scope.ContributionModelForView);
					$scope.data.$promise.then(function(result) {
						alert('Contribution closed');
						$location.path("/contributions");
					});

				};
				function init() {					

					vm.fields = [ {
						type : 'input',
						key : 'title',
						templateOptions : {
							label : 'Title:'
						}
					}, {
						type : 'input',
						key : 'file',
						templateOptions : {
							label : 'File'
						}
					}, {
						type : 'repeatSection',
						key : 'contributers',
						templateOptions : {
							btnText : 'Add another Contributer',
							required : true,
							fields : [ {
								className : 'row',
								fieldGroup : [ {
									key : 'contributer_id',
									className : 'col-xs-4',
									type : 'select',
									templateOptions : {
										label : 'Contributer',
										labelProp : 'name',
										valueProp : 'id',
										options : vm.users
									}
								}, {
									type : 'input',
									key : 'contributer_percentage',
									className : 'col-xs-4',
									templateOptions : {
										label : 'Contributer Percentage:',
									}
								}

								]
							} ]
						}
					}

					];

				}

				if ($auth.isAuthenticated()) {
					$scope.contributions = Contributions.getAllContributions({
						organizationId : $scope.organizationId
					});
				}

			}

		});
