angular.module('MyApp').controller(
		'ContributionsCtrl',
		function($scope, $auth, $location, $stateParams, $alert, Contributions,
				ContributionDetail, SaveContribution, CloseContribution,
				Account, Users) {			
			var orgExists;
			$scope.currencyFormatting = function(value) { return value.toString() + " $"; };
			$scope.organizationId = 'notintialized';
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
				
				$scope.updateContributer = function(selectedUserId,index) {
					console.log('comes here firt')
					urlImage = ''
					for(i = 0 ; i<$scope.users.length ; i++){						
						if($scope.users[i].id == selectedUserId ){
							urlImage =  $scope.users[i].url
							break;
						}
					}
					for(j=0;j<$scope.model.contributers.length ; j++){
						console.log(' $scope.model.contributers[j].contributer_id:' +  $scope.model.contributers[j].contributer_id)
						if(selectedUserId == $scope.model.contributers[j].contributer_id && $scope.model.contributers[j].contributer_percentage != ''){
							$scope.model.contributers[index].contributer_id = 0	
							$scope.model.contributers[index].img = 'images/avatar.jpg'
							$scope.model.contributers[index].contributer_percentage = ''
							$scope.model.contributers[index].contribution1 = 50
							$scope.changeContribution();
							alert('This collbrator is already beend added')
							return '';
						}
					}
					$scope.changeContribution();
					return urlImage;
					
					
				};


				$scope.getOrgUsers = function() {
					$scope.data = Users.getOrg.getUsers({
						organizationId : $scope.organizationId
					});
					$scope.data.$promise.then(function(result) {
						Users.setAllOrgUsersData(result)						
						$scope.users = result;						
						//$location.path("/contribution/" + result.id);
					});
				};

				allOrgUsersData = Users.getAllOrgUsersData();
				if (orgExists == 'true') {
					if (allOrgUsersData == undefined) {
						$scope.getOrgUsers();
					} else {

						$scope.users = allOrgUsersData;
					}
				}

				$scope.contributionId = $stateParams.contributionId;

				$scope.ContributionModelForView = {
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
				
				$scope.changeContribution = function() {
					totalContribution = 0;
					console.log('comes here in change')
					allcontributers = $scope.model.contributers
					for(i=0;i<allcontributers.length;i++){
						if(allcontributers[i].contributer_id != 0){
							totalContribution = totalContribution + +allcontributers[i].contribution1;
						}
						
						
						
					}
					
					for(i=0;i<allcontributers.length;i++){
						if(allcontributers[i].contributer_id != 0){
							allcontributers[i].contributer_percentage = (allcontributers[i].contribution1/totalContribution)*100
						}
						
						
						
					}

				};


				// function definition
				$scope.onSubmit = function() {
					console.log("In Submit method");
					console.log($scope.model)
					$scope.data = SaveContribution.save({}, $scope.model);
					$scope.data.$promise.then(function(result) {
						alert('Successfully saved');
						$location.path("/bids/" + result.id);
					});
				};
				
				$scope.removeCollaboratorItem = function(index) {
					
					$scope.model.contributers.splice(index, 1);
					for(j=0;j<$scope.model.contributers.length ; j++){
						console.log(' $scope.model.contributers[j].contributer_id:' +  $scope.model.contributers[j].contributer_id)
					}
					$scope.changeContribution();
			  };
				$scope.createContribution = function() {
					console.log("Create Contribution");
					console.log($scope.model);
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
				

				if ($scope.contributionId && $scope.contributionId != 0) {
					$scope.data1 = ContributionDetail.getDetail({
						contributionId : $scope.contributionId
					});
					$scope.data1.$promise.then(function(result) {
						$scope.ContributionModelForView = result;
					});
				}
				//$scope.users = User.query();
				$scope.orderProp = "time_created"; // set initial order criteria
				$scope.addCollaborator = function() {
					
					
					
					$scope.model.contributers.push({
						contributer_id:'0',
						contributer_percentage:'',
						contribution1:'50',
						img:'images/avatar.jpg'
					}) ;
				};
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

				if ($auth.isAuthenticated()) {
					$scope.contributions = Contributions.getAllContributions({
						organizationId : $scope.organizationId
					});
				}

			}

		});
