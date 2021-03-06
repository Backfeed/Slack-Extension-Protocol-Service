angular.module('MyApp', ['uiSlider','ngResource', 'ngMessages', 'ui.router', 'mgcrea.ngStrap', 'satellizer','BFAPIServices'])
  .config(function($stateProvider, $urlRouterProvider, $authProvider) {
    $stateProvider
	  .state('extPopUp', {
		controller: 'ExtPopUpCtrl',
        url: '/extPopUp',
        templateUrl: 'partials/extPopUp.html'
	  })
	  .state('splash', {
		controller: 'SplashCtrl',
        url: '/splash',
        templateUrl: 'partials/splash.html'
      })
      .state('contributionDetail', {
        url: '/contribution/:contributionId',
        templateUrl: 'partials/contributionDetail.html',
        controller: 'ContributionsCtrl'
      })
      .state('createContribution', {
        url: '/contribution',
        templateUrl: 'partials/createContribution.html',
        controller: 'ContributionsCtrl'
      })
      .state('createOrg', {
        url: '/organization',
        templateUrl: 'partials/createOrganization.html',
        controller: 'OrganizationCtrl'
      })
      .state('contributionStatus', {
    	  url: '/contributionStatus/:contributionId',
        templateUrl: 'partials/contributionStatus.html',
        controller: 'ContributionStatusCtrl'
      })
	  .state('contributions', {
		controller: 'ContributionsCtrl',
        url: '/contributions',
        templateUrl: 'partials/contributions.html'
      })
      .state('bids', {
        url: '/bids/:contributionId',
        templateUrl: 'partials/createBid.html',
        controller: 'BidsCtrl'
      })
	  .state('users', {
		controller: 'UsersCtrl',
        url: '/users',
        templateUrl: 'partials/users.html'
      })
       .state('orgs', {
		controller: 'OrganizationCtrl',
        url: '/orgs',
        templateUrl: 'partials/orgs.html'
      })
     .state('userDetail', {
        url: '/user/:userId',
        templateUrl: 'partials/userDetail.html',
        controller: 'UsersCtrl'
      })
      .state('createUser', {
        url: '/user',
        templateUrl: 'partials/createUser.html',
        controller: 'UsersCtrl'
      })
      
      .state('login', {
        url: '/login',
        templateUrl: 'partials/login.html',
        controller: 'LoginCtrl'
      })
      .state('signup', {
        url: '/signup',
        templateUrl: 'partials/signup.html',
        controller: 'SignupCtrl'
      })
      .state('logout', {
        url: '/logout',
        template: null,
        controller: 'LogoutCtrl'
      })
      .state('profile', {
        url: '/profile',
        templateUrl: 'partials/profile.html',
        controller: 'ProfileCtrl',
        resolve: {
          authenticated: function($q, $location, $auth) {
            var deferred = $q.defer();

            if (!$auth.isAuthenticated()) {
              $location.path('/splash');
            } else {
              deferred.resolve();
            }
            return deferred.promise;
          }
        }
      });

    $urlRouterProvider.otherwise('/contributions');

	$authProvider.slack({
      clientId: '3655944058.8209971669'
    });
   
  });
