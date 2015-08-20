angular.module('MyApp')
  .controller('OrganizationCtrl', function($scope,$auth,$alert,$location,$stateParams,SaveOrg,Account,Users,AllSlackUsers,CheckOrgTokenName,AllOrgs,CheckOrgCode) {
	  $scope.userData= ''
      $scope.validationFailureForTokenName = false;
	  $scope.validationFailureForCode = false;
	
	  $scope.orgModel = {
				token_name : '',
				slack_teamid : '',				
				name : '',
				code : '',
				token : '',
				channelName :'',
				contributers : [ {
					contributer_id : '0',
					contributer_percentage : '',
					contribution1: '50',
					img:'images/avatar.jpg',
					usersList:[]
				} ]

			}
	  $scope.getOrgUsers = function() {
		    $scope.data = AllSlackUsers.allSlackUsers();
			$scope.data.$promise.then(function(result) {
				$scope.users = result;	
				$scope.orgModel.contributers[0].usersList = $scope.users;
				//$location.path("/contribution/" + result.id);
			});
		};
	  $scope.getOrgUsers();
	  $scope.organizations = AllOrgs.allOrgs();
	  
	 
	  
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
			 $scope.getOrgUsers();
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
   
   
   
   $scope.updateContributer = function(selectedUserId,index) {
		console.log('comes here firt')
		urlImage = ''
		for(i = 0 ; i<$scope.users.length ; i++){						
			if($scope.users[i].id == selectedUserId ){
				urlImage =  $scope.users[i].url
				break;
			}
		}					
		
		$scope.changeContribution();
		return urlImage;
		
		
	};
	
	
	
	$scope.changeContribution = function() {
		totalContribution = 0;
		allcontributers = $scope.orgModel.contributers
		valid = true;
		if(allcontributers.length){
			valid = false;	
		}
		for(i=0;i<allcontributers.length;i++){
			if(allcontributers[i].contributer_id != 0){
				totalContribution = totalContribution + +allcontributers[i].contribution1;
			}else{
				valid = false;							
			}
			
			
			
		}
		
		for(i=0;i<allcontributers.length;i++){
			if(allcontributers[i].contributer_id != 0){
				allcontributers[i].contributer_percentage = (allcontributers[i].contribution1/totalContribution)*100
			}
			
			
			
		}
		
		$scope.buttonDisabled = valid;

	};
	
	$scope.removeCollaboratorItem = function(index) {
		$scope.orgModel.contributers.splice(index, 1);						
		$scope.changeContribution();
  };
  
  $scope.addCollaborator = function() {
	  	console.log('comes here in add');
		allcontributers = $scope.orgModel.contributers							
		newUserList = [];
		for(i = 0 ; i<$scope.users.length ; i++){
			userExist = false;
			for(j=0;j<allcontributers.length;j++){
				if($scope.users[i].id == allcontributers[j].contributer_id ){
					userExist = true;
					break;
				}
			}
			if(userExist == false){
				newUserList.push($scope.users[i]);
			}
		}																
		$scope.orgModel.contributers.push({
			contributer_id:'0',
			contributer_percentage:'',
			contribution1:'50',
			img:'images/avatar.jpg',
			usersList:newUserList
		}) ;
		$scope.buttonDisabled = true;
	};
   
   
   $scope.checkTokenName = function(){
	   if($scope.orgModel.token_name != ''){
		   $scope.data1 = CheckOrgTokenName.checkOrgTokenName({
			   tokenName : $scope.orgModel.token_name
			});
			$scope.data1.$promise.then(function(result) {
				console.log('this is it');				
				if(result.tokenAlreadyExist == 'true'){
					$scope.validationFailureForTokenName = true;
				}else{
					$scope.validationFailureForTokenName = false;
				}
			});
	   }
	   
	  
   }
   
   $scope.checkCode = function(){
	   if($scope.orgModel.code != ''){
		   $scope.data1 = CheckOrgCode.checkOrgCode({
			   code : $scope.orgModel.code
			});
			$scope.data1.$promise.then(function(result) {
				console.log('this is it');				
				if(result.codeAlreadyExist == 'true'){
					$scope.validationFailureForCode = true;
				}else{
					$scope.validationFailureForCode = false;
				}
			});
	   }
	   
	  
   }
   
   $scope.orderProp = "name";
	$scope.submit = function(){
		if($scope.validationFailureForTokenName == true){
			alert('This name is already taken please use other')
			return
		}
		if($scope.validationFailureForCode == true){
			alert('This code is already taken please use other')
			return
		}
		console.log("In Submit method");
		console.log($scope.orgModel)
		$scope.data = SaveOrg.save({},$scope.orgModel);
		$scope.data.$promise.then(function (result) {
			if(result.channelExists == 'true'){
				alert('Channel '+$scope.orgModel.channelName+' already exists. Please choose another');
				return;
			}
			if(result.id == 0){
				alert('This code or name is already taken please use other')
				return;
			}			
			
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