angular.module('MyApp', ['ngResource', 'ngMessages', 'ui.router', 'mgcrea.ngStrap', 'satellizer','BFAPIServices','formly','formlyBootstrap'])
  .config(function($stateProvider, $urlRouterProvider, $authProvider) {
    $stateProvider
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
      clientId: '2969711723.3476875864'
    });

  });
