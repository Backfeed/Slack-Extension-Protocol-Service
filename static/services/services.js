'use strict';
var bfAPIServices = angular.module('BFAPIServices', [ 'ngResource' ]);

bfAPIServices.factory('Contributions', [ '$resource', function($resource) {
	return $resource('contribution/all/:organizationId', {}, {
		getAllContributions : {
			method : 'GET',
			params : {},
			isArray : true
		}
	});
} ]);

bfAPIServices.factory('ContributionDetail', [ '$resource', function($resource) {
	return $resource('contribution/:contributionId', {}, {
		getDetail : {
			method : 'GET',
			params : {},
			isArray : false
		}
	});
} ]);

bfAPIServices.factory('SaveContribution', [ '$resource', function($resource) {
	return $resource('contribution', {}, {
		save : {
			method : 'POST',
			params : {},
			isArray : false
		}
	});
} ]);
bfAPIServices.factory('CloseContribution', [ '$resource', function($resource) {
	return $resource('contribution/close', {}, {
		save : {
			method : 'POST',
			params : {},
			isArray : false
		}
	});
} ]);
bfAPIServices.factory('SaveBidTOContribution', [ '$resource',function($resource) {
	return $resource('bids', {}, {
		save : {
			method : 'POST',
			params : {},
			isArray : false
		}
	});
} ]);
bfAPIServices.factory('Users', [ '$resource', function($resource) {
	var allOrgUsersData;		 
			return {getOrg :$resource('users/all/:organizationId', {}, {
			getUsers: {
				method : 'GET',
				params : {},
				isArray : true
		}
	}),getAllOrgUsersData: function() {return allOrgUsersData},
	 setAllOrgUsersData: function(data) {		
		allOrgUsersData = data;
    },};
} ]);
	
bfAPIServices.factory('UserDetail', [ '$resource', function($resource) {
	return $resource('users/:userId/:organizationId', {}, {
		getDetail : {
			method : 'GET',
			params : {},
			isArray : false
		}
	});
} ]);

bfAPIServices.factory('SaveUser', [ '$resource', function($resource) {
	return $resource('users', {}, {
		save : {
			method : 'POST',
			params : {},
			isArray : false
		}
	});
} ]);

bfAPIServices.factory('ContributionStatus', [ '$resource', function($resource) {
	return $resource('contribution/status/:id/:userId', {}, {
		getDetail : {
			method : 'GET',
			params : {},
			isArray : false
		}
	});
} ]);

bfAPIServices.factory('SaveOrg', [ '$resource', function($resource) {
	return $resource('organization', {}, {
		save : {
			method : 'POST',
			params : {},
			isArray : false
		}
	});
} ]);

bfAPIServices.factory('CheckOrgTokenName', [ '$resource', function($resource) {
	return $resource('organization/checkTokenName/:tokenName', {}, {
		checkOrgTokenName : {
			method : 'GET',
			params : {},
			isArray : false
		}
	});
} ]);

bfAPIServices.factory('CheckOrgCode', [ '$resource', function($resource) {
	return $resource('organization/checkCode/:code', {}, {
		checkOrgCode : {
			method : 'GET',
			params : {},
			isArray : false
		}
	});
} ]);


bfAPIServices.factory('AllSlackUsers', [ '$resource', function($resource) {
	return $resource('allSlackUsers', {}, {
		allSlackUsers : {
			method : 'GET',
			params : {},
			isArray : true
		}
	});
} ]);

bfAPIServices.factory('AllOrgs', [ '$resource', function($resource) {
	return $resource('organization/all', {}, {
		allOrgs : {
			method : 'GET',
			params : {},
			isArray : true
		}
	});
} ]);
