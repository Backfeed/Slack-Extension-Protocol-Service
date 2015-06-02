(function() {
    var lib_path = '/rhizi/lib/';
    var config = {
        shim: {
            'socketio': { exports: 'io' },
        },
        paths: {
            autocomplete: lib_path + 'autocomplete',
            caret: lib_path + 'caret',
            Bacon: lib_path + 'Bacon',
            'd3': lib_path + 'd3/d3',
            FileSaver: lib_path + 'FileSaver',
            jquery: lib_path + 'jquery',
            'jquery-ui': lib_path + 'jquery-ui',
		//	'jquery-multiselect':lib_path+'jquery.multiselect.min',
            socketio: lib_path + 'socket.io/socket.io.min_0.9.10',
            html2canvas: lib_path + 'html2canvas',
            feedback: lib_path + 'feedback',
        }
    }

    config.urlArgs = (typeof local_config != 'undefined') && local_config.urlArgs;

if (window.is_node) {
    // Testing path only
    console.log('app: running under node');
    config.baseUrl = '../src/';
    window.rhizi_require_config = config;
} else {
    // [!] no need to configure baseUrl, as in
    //     config.baseUrl = ...
    //     generated script URLs include the basepath of app.js

    // Main app path
    require.config(config);

    requirejs(['main'], function(main) {
        console.log('starting rhizi logic');
        main.main();
    });
}
}());


		//	'jquery-multiselect':lib_path+'jquery.multiselect.min',