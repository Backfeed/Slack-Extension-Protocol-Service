define(function() {
	var HOST = 'localhost'
	//var HOST = 'deap-env.elasticbeanstalk.com'
    
	//var PORT = '80'
	var PORT = '3000'
	
	return {
        'rand_id_generator' : 'hash',
        'rz_server_host': HOST,
        'rz_server_port': PORT,
        'backend_enabled': true,
        'backend__maintain_ws_connection': true,
        'feedback_url': '/feedback',
    };
});
