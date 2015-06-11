angular.module('MyApp').controller(
		'ContributionsCtrl',
		function($scope, $auth, $location, $stateParams, $alert, Contributions,
				ContributionDetail, SaveContribution, CloseContribution,
				Account, Users) {
			var vm = this;
			vm.model = {
					title : '',
					file : '',
					owner : '',
					min_reputation_to_close : '',
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
				
				vm.getUsers = function() {
					$scope.data = Users.getUsers1.getUsers();
					$scope.data.$promise.then(function(result) {
						Users.setAllUsersData(result)
						console.log("this is result"+result[0].id);
						vm.users = result;
						init();
						//$location.path("/contribution/" + result.id);
					});
				};
				allUsersData = Users.getAllUsersData();
				console.log("allUsersData is" + allUsersData);
				if (allUsersData == undefined) {
					vm.getUsers();
				} else {
					
					vm.users = allUsersData;
					init();
				}
				
				
				vm.contributionId = $stateParams.contributionId;
				vm.getProfile = function() {
					Account.getProfile().success(function(data) {
						$scope.userId = data.userId;
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
				vm.contributionId = $stateParams.contributionId;
				userData = Account.getUserData();
				console.log("userData is" + userData);
				if (userData == undefined) {
					vm.getProfile();
				} else {
					vm.userId = userData.userId;
					vm.model.owner = userData.userId;
				}

				vm.ContributionModelForView = {
					title : '',
					file : '',
					owner : '',
					min_reputation_to_close : '',
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
				if ($auth.isAuthenticated()) {
					$scope.contributions = Contributions.getAllContributions();
				}

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
					console.log("After Init"+vm.users)
					
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
						type : 'input',
						key : 'min_reputation_to_close',
						templateOptions : {
							label : 'Min Reputation To Close'
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
										valueProp :'id',
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
					}, {
						type : 'repeatSection',
						key : 'intialBid',
						templateOptions : {
							btnText : '',
							fields : [ {
								className : 'row',
								fieldGroup : [ {
									className : 'col-xs-4',
									type : 'input',
									key : 'tokens',
									templateOptions : {
										label : 'Tokens Id:'
									}
								}, {
									type : 'input',
									key : 'reputation',
									className : 'col-xs-4',
									templateOptions : {
										label : 'Reputation:',
									}

								} ]
							} ]
						}
					}

					];

				}

			}

		});
