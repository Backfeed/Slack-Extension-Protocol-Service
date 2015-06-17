angular.module('MyApp')
  .controller('OrganizationCtrl', function($scope,$auth,$alert,$location,$stateParams,SaveOrg,Account,Users,AllSlackUsers,CheckOrgTokenName) {
	  $scope.userData= ''
      $scope.validationFailure = false;
	  $scope.showContributer = false;
	  $scope.getOrgUsers = function() {
			$scope.data = AllSlackUsers.allSlackUsers();
			$scope.data.$promise.then(function(result) {
				$scope.allUsers = result;
				//$location.path("/contribution/" + result.id);
			});
		};
	
	  $scope.orgModel = {
				token_name : '',
				slack_teamid : '',
				intial_tokens : '',
				contributers : [ {
					contributer_id : '',
					contributer_percentage : '',
					contribution1: '',
					token: '',
					reputation: ''
				} ],
				name : ''

			}
	  $scope.getOrgUsers();
	  $scope.removeCollaboratorItem = function(index) {
			$scope.orgModel.contributers.splice(index, 1);
	  };
	  $scope.changeContribution = function() {
			totalContribution = 0;
			allcontributers = $scope.orgModel.contributers
			for(i=0;i<allcontributers.length;i++){
				totalContribution = totalContribution + +allcontributers[i].contribution1;
				
				
			}
			
			for(i=0;i<allcontributers.length;i++){
				allcontributers[i].contributer_percentage = (allcontributers[i].contribution1/totalContribution)*100;
				allcontributers[i].token = ($scope.orgModel.intial_tokens * allcontributers[i].contributer_percentage)/100;
				allcontributers[i].reputation = ($scope.orgModel.intial_tokens * allcontributers[i].contributer_percentage)/100;
				
			}

		};
	  $scope.getProfile = function() {
	      Account.getProfile()
	        .success(function(data) {
				Account.setUserData(data);
				$scope.userData = Account.getUserData();
				alert($scope.userData)
				
	        })
	        .error(function(error) {
	        $alert({
	            content: error.message,
	            animation: 'fadeZoomFadeDown',
	            type: 'material',
	            duration: 3
	          });
	        });
	    };	    
	     $scope.userData = Account.getUserData();
		 console.log("userData is"+$scope.userData);
		 if($scope.userData == undefined){
			 $scope.getProfile();
		 }else{
			 $scope.userId = $scope.userData.userId;
			 $scope.orgModel.name = $scope.userData.slackTeamName;
			 $scope.orgModel.slack_teamid = $scope.userData.slackTeamId;
		 }
	// if not authenticated return to splash:
	if(!$auth.isAuthenticated()){
		$location.path('splash'); 
    }

	//$scope.slackUsers = Users.getUsers();
  
   
	
   
   $scope.changeTeam = function(){
	   console.log('comes here in logout')
	   $location.path("/logout");
	   
   };
   
   
   
   $scope.checkTokenName = function(){
	   if($scope.orgModel.token_name != ''){
		   $scope.data1 = CheckOrgTokenName.checkOrgTokenName({
			   tokenName : $scope.orgModel.token_name
			});
			$scope.data1.$promise.then(function(result) {
				console.log('this is it');				
				if(result.tokenAlreadyExist == 'true'){
					$scope.validationFailure = true;
				}else{
					$scope.validationFailure = false;
				}
			});
	   }
	   
	  
   }
   
   $scope.checkTokens = function(){
	   console.log('$scope.orgModel.intial_tokens:' +$scope.orgModel.intial_tokens)
	   if($scope.orgModel.intial_tokens != ''){
		   $scope.showContributer = true;
		}else{
			$scope.showContributer = false;
		}
	   
	  
   }
   $scope.addCollaborator = function() {
		$scope.orgModel.contributers.push({
			contributer_id:'',
			contributer_percentage:'',
			contribution1:'',
			token: '',
			reputation: ''
		}) ;
	};
	$scope.submit = function(){
		console.log("In Submit method");
		console.log($scope.orgModel)
		$scope.data = SaveOrg.save({},$scope.orgModel);
		$scope.data.$promise.then(function (result) {
		
			$scope.userData.orgId = result.organization_id;
			$scope.userData.userOrgId = result.id;
			$scope.userData.orgexists = "true";
			console.log('Inserted org id : '+result.organization_id)
			console.log('Inserted userorg id : '+result.id)
		 	Account.setUserData($scope.userData);
			alert('Successfully created organization');
			$location.path("/contribution"); 
			
		});
		
		
		
		
		
	};
	
	
});