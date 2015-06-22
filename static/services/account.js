angular.module('MyApp')
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
	
	.factory('CTagKey', function ($rootScope) {
	  var extractedCTags = [];
	  var userCreatedCTags = [];
	  var query = '';
	  var cTags = []; 
	//	console.log('INIT:  this.cTags'+this.cTags);

	  var addCTag = function (cTag) {
			userCreatedCTags.push(cTag);
			//console.log('extractedCTags:'+extractedCTags);
			this.cTags = extractedCTags.concat(userCreatedCTags);
	  };

	  var removeCTag = 	function (cTag) {
		//debugger;
		// TBD: if removing from extracted tags list it so next query analysis we wont create it again
			console.log('going to remove  cTag.text:'+cTag.text+'cTags:'+this.cTags);

			for (var i = 0; i < userCreatedCTags.length; i++) {
			    var ctag = userCreatedCTags[i];
			    if(ctag && ctag.text === cTag.text){
					userCreatedCTags.splice(i, 1);
				}
			}
			for (var i = 0; i < extractedCTags.length; i++) {
			    var ctag = extractedCTags[i];
			    if(ctag && ctag.text === cTag.text){
					extractedCTags.splice(i, 1);
				}
			}
	  };

	  return {
	    analyzeQuery: function (query, callback) {
			this.query = query;
	      // TBD: use backend module  instead ?
			// reset tags:
			 extractedCTags = [];


			// extract Capital starting Words from Query:
			var words = query.split(" ");

			var arrayLength = words.length;
			for (var i = 0; i < arrayLength; i++) {
			    var word = words[i];
			    if(word[0] && word[0] === word[0].toUpperCase()){
					extractedCTags.push({text:word});
				}
			}
			this.cTags = extractedCTags.concat(userCreatedCTags);
			console.log('this.cTags'+this.cTags);
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
	    cTags: cTags,
		addCTag: addCTag,
		removeCTag:removeCTag,
		resetCTag: function () {
	  		// reset tags:
			var extractedCTags = [];
	    },
		query:query
	  };
	});


