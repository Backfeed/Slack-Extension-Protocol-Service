angular.module('MyApp')
  .controller('OrganizationCtrl', function($scope,$auth,$alert,$location,$stateParams,SaveOrg,Account) {
	  var vm = this;
	  vm.orgModel = {
				token_name : '',
				slack_teamid : '',
				intial_tokens : '',
				name : ''

			}
	  $scope.getProfile = function() {
	      Account.getProfile()
	        .success(function(data) {
				Account.setUserData(data);
				
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
	     userData = Account.getUserData();
		 console.log("userData is"+userData);
		 if(userData == undefined){
			 $scope.getProfile();
		 }else{
			 vm.userId = userData.userId;
			 vm.orgModel.name = userData.slackTeamName;
			 vm.orgModel.slack_teamid = userData.slackTeamId;
		 }
	// if not authenticated return to splash:
	if(!$auth.isAuthenticated()){
		$location.path('splash'); 
    }

	//$scope.slackUsers = Users.getUsers();
  
   
	
   vm.orgFields = [
                      {
                          key: 'token_name',
                          type: 'input',
                          templateOptions: {
                              type: 'text',
                              label: 'Token Name',
                              placeholder: 'Enter Token Name',
                              required: true
                          }
                      },
                      {
                          key: 'intial_tokens',
                          type: 'input',
                          templateOptions: {
                              type: 'text',
                              label: 'Intial Tokens',
                              placeholder: 'Enter Intial Tokens',
                              required: true
                          }
                      }
                  ];
                  
          
	
	vm.submit = function(){
		console.log("In Submit method");
		console.log(vm.orgModel)
		vm.data = SaveOrg.save({},vm.orgModel);
		vm.data.$promise.then(function (result) {
			
			userData.orgId = result.organization_id;
			userData.userOrgId = result.id;
		    userData.orgexists = "true";
			console.log('Inserted org id : '+result.organization_id)
			console.log('Inserted userorg id : '+result.id)
		 	Account.setUserData(userData);
			alert('Successfully created organization');
			$location.path("/contributions"); 
			
		});
		
		
		
		
		
	};
	
	
});