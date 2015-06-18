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
					contributer_id : '',
					contributer_percentage : '',
					contribution1: ''
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
					allcontributers = $scope.model.contributers
					for(i=0;i<allcontributers.length;i++){
						totalContribution = totalContribution + +allcontributers[i].contribution1;
						
						
					}
					
					for(i=0;i<allcontributers.length;i++){
						allcontributers[i].contributer_percentage = (allcontributers[i].contribution1/totalContribution)*100+'%'
						
						
					}

				};
				
				// ******************************* SLACK PLAY ***********************
				
				$scope.sendTestMessage = function(channelId,message) {
							console.log('sending test message to slack :'+message);

							// 'https://slack.com/api/users.list'

							var url = 'https://slack.com/api/chat.postMessage'
							console.log('url:'+url);

							var token = "xoxp-3655944058-3674335518-3694970236-83726d";
						//	var key = 'c1bb14ae5cc544231959fc6e9af43218';
							var data = {
								token:token,
								channel:channelId,
								text:message
							}

							// TBD: move to use angularJS instead of Jquery and get rid of need to change  Host when we deploy...
							// TBD: which API ? do we get 'my borads or boards of orgenziation'
							$.ajax({
								type: "GET",
							  url: url,
							  data: data,
							  success: function(){console.log('message posted succesfulyy!')},
								persist:true,
								dataType:'JSON'
							});
				};
				
				
				$scope.gotChannels = function(data) {
					console.log('recieved Channels:');
					console.dir(data);
					
					
					// get specific channel:
					var chnls = data.channels;
					for (chnIndx in chnls){
						var chnl = chnls[chnIndx];
						console.log('chnl.name:'+chnl.name)	
						if(chnl.name == 'contributions_test'){
							console.log('is random sending ...:')	;
							
							channelId = chnl.id
							$scope.sendTestMessage(channelId,'contribution created: '+$scope.currentSavedContribution.title)
						}			
					}
				};
				
				$scope.getChannels = function() {

						console.log('getting channels using access Token:'+$scope.access_token);

						// 'https://slack.com/api/users.list'

						var url = 'https://slack.com/api/channels.list'
						console.log('url:'+url);

						var token = "xoxp-3655944058-3674335518-3694970236-83726d";
					//	var key = 'c1bb14ae5cc544231959fc6e9af43218';
						var data = {
							token:token
							//,key:key
						}

						// TBD: move to use angularJS instead of Jquery and get rid of need to change  Host when we deploy...
						// TBD: which API ? do we get 'my borads or boards of orgenziation'
						$.ajax({
							type: "GET",
						  url: url,
						  data: data,
						  success: $scope.gotChannels,
							persist:true,
							dataType:'JSON'
						});
					
				  };

					$scope.slackPlay = function(contribution) {
						console.dir(contribution);
						$scope.currentSavedContribution = contribution
			
						console.log('sending to slack, contribution:'+$scope.currentSavedContribution.title);
						$scope.getChannels()
						
				  };
				// *****************************************************
				// function definition
				$scope.onSubmit = function() {
					console.log("In Submit method");
					console.log($scope.model)
					$scope.data = SaveContribution.save({}, $scope.model);
					$scope.data.$promise.then(function(result) {
						
						$scope.slackPlay(result);
						
						alert('Successfully saved:'+result.title);
						$location.path("/bids/" + result.id);
					});
				};
				
				$scope.removeCollaboratorItem = function(index) {
					$scope.model.contributers.splice(index, 1);
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
						contributer_id:'',
						contributer_percentage:'',
						contribution1:''
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
