angular.module('MyApp')
	.factory('Users', function($http,Const) {
		 console.log('loading Users into system.');
		 var users
	
		var setUsers       = function (usersIn) {
				for (i in usersIn){
					usersIn[i].type = Const.NODE_TYPE_PERSON;
				}
				users            = usersIn;
		}
		
	
		//var users        = $http.get('/api/users');
		/*
	 	$http.get('/api/deapusers').
		  success(function(data, status, headers, config) {
		    // this callback will be called asynchronously
		    // when the response is available
	 			
	
				setUsers(data.json_list);
				console.log('users loaded:');
				console.dir(users);		  
			}).
		  error(function(data, status, headers, config) {
		    // called asynchronously if an error occurs
		    // or server returns response with an error status.
			console.log('Users:get deap Users:error:'+data);
		  });
		*/

		 return {
		   	setUsers: setUsers,
		    getUsers: function() {
		     	return users;
		   }
		 }
	})

	.factory('Account', function($http) {
		
		var userData;
		
	  return {
	    getProfile: function() {
	      return $http.get('/api/me');
	    },
	    updateProfile: function(profileData) {
	      return $http.post('/api/updateMe', profileData);
	    },
	
		// TBD: hold all account info here to be access from all controllers not only Profile controller
		setUserData: function(data) {
			console.log('setUserData:');
			console.dir(data);
	       userData = data;
	    },
		getUserData:function(){
			return userData;
		}
	
	  };
	})

.factory('Query', function ($http,$state) {
  var extractedHTags = [];
  var query = '';
  var hTags = []; 
  var results = [];



  return {
	setQuery: function(query) {
		console.log('execute: query:'+query);
		this.query = query;
	    //this.results = $http.post('/api/query', {'query':query});
	},
	getQuery: function() {
	 	return 	this.query;
	    //
	},
	getResults: function(callback) {
		this.results = $http.post('/api/query', {'query':this.query}).
		  success(function(data, status, headers, config) {
		    // this callback will be called asynchronously
		    // when the response is available
			console.log('query succeded.');
			callback();
		  }).
		  error(function(data, status, headers, config) {
		    // called asynchronously if an error occurs
		    // or server returns response with an error status.
			console.log('query failed.');
		  });
		 
		
	     return this.results;
		
	},
    analyzeQuery: function (query, callback) {
		this.query = query;
      // TBD: use backend module  instead ?
		// reset tags:
		 extractedHTags = [];

		
		// extract Capital starting Words from Query:
		var words = query.split(" ");
		
		var arrayLength = words.length;
		for (var i = 0; i < arrayLength; i++) {
		    var word = words[i];
		    if(word[0] && word[0] === word[0].toUpperCase()){
				extractedHTags.push({text:word});
			}
		}
		console.log('this.hTags'+this.hTags);
    },
	loadAutoComplete: function (tagQuery) {
		var words =  this.query.split(" ");
		var autocompleteValues = [];
		var arrayLength = words.length;
		for (var i = 0; i < arrayLength; i++) {
		    var word = words[i];
		 
			autocompleteValues.push(word);
			
		}
		console.log('auticomplete values:'+autocompleteValues);
		var p5 = new Promise(function(resolve, reject) { resolve(autocompleteValues) ;});
		return p5;
		
    },

	resetCTag: function () {
  		// reset tags:
		var extractedHTags = [];
    }
  };
});

;