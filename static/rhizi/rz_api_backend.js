"use strict";

/**
 * API calls designed to execute against a local backend service
 */
define([ 'rz_config' ], function(rz_config) {

    function RZ_API_Backend() {

		// set call URL:
        var rz_server_url = 'http://' + rz_config.rz_server_host + ':'
                + rz_config.rz_server_port;

		// Add spinner:
        var opts = {
          lines: 13, // The number of lines to draw
          length: 20, // The length of each line
          width: 10, // The line thickness
          radius: 30, // The radius of the inner circle
          corners: 1, // Corner roundness (0..1)
          rotate: 0, // The rotation offset
          direction: 1, // 1: clockwise, -1: counterclockwise
          color: '#000', // #rgb or #rrggbb or array of colors
          speed: 1, // Rounds per second
          trail: 60, // Afterglow percentage
          shadow: false, // Whether to render a shadow
          hwaccel: false, // Whether to use hardware acceleration
          className: 'spinner', // The CSS class to assign to the spinner
          zIndex: 2e9, // The z-index (defaults to 2000000000)
          top: '50%', // Top position relative to parent
          left: '50%' // Left position relative to parent
        };
		var spinner = new Spinner(opts);



        /**
         * issue rhizi server ajax call
         */
        var ajax_rs = function(path, req_opts, on_success, on_error) {

            function on_error_wrapper(xhr, err_text, err_thrown) {
                spinner.stop();

				// log wrap callback
                console.error('error: \'' + err_text + '\'');
                if (on_error && typeof (on_error) === "function") {
                    on_error(err_text);
                }

				alert('sorry, an error has occured: \'' + err_text + '\'')
            }

            function on_success_wrapper(xhr, text) {
				spinner.stop();
				
                // log wrap callback
                var ret_data = xhr.data,
                    ret_error = xhr.error;
                if (ret_error) {
                    console.log('ajax error: ' + JSON.stringify(ret_error));
                    if (on_error) {
                        on_error(ret_error);
                    }
                } else {
                    
                    console.log('ajax success: ' + JSON.stringify(ret_data));
                    if (on_success) {
                        on_success(ret_data);
                    }
                }
            }

			// get Auth Header: check if user is authenticated: (get satellizer token from localstorage):
			var satAuthToken = localStorage.getItem('satellizer_token');
			var headers =  {}
			if (satAuthToken){
				headers =  { 'x-access-token': 'Bearer '+satAuthToken }
			}
			
			/*
             * add common request options
             */

            req_opts.dataType = "json";
            req_opts.contentType = "application/json; charset=utf-8";
            req_opts.error = on_error_wrapper;
            req_opts.success = on_success_wrapper;
            req_opts.headers = headers;
            req_opts.timeout = 30000; // ms
            req_opts.crossDomain = true;
			
			console.log('ajax_rs: sending req , path:' + path);

            $.ajax(rz_server_url + path, req_opts);
			
			// spin:
			var target = document.getElementById('spinner');
	        spinner.spin(target);
        }

        /**
         * common attr_diff
         */
        this.commit_diff__attr = function(attr_diff, on_success, on_error) {

            var post_dict = {
                'attr_diff' : attr_diff
            }

            var req_opts = {
                type : 'POST',
                data : JSON.stringify(post_dict),
            };

            return ajax_rs('/graph/diff-commit-attr', req_opts, on_success,
                    on_error);
        }

        /**
         * commit topo_diff
         */
        this.commit_diff__topo = function(topo_diff, on_success, on_error) {

            var post_dict = {
                'topo_diff' : topo_diff
            }

            var req_opts = {
                type : 'POST',
                data : JSON.stringify(post_dict),
            };

            return ajax_rs('/graph/diff-commit-topo', req_opts, on_success,
                    on_error);
        }

        /**
         * commit vis_diff
         */
        this.commit_diff__vis = function(vis_diff, on_success, on_error) {
            var post_dict = {
                'vis_diff' : vis_diff
            }

            var req_opts = {
                type : 'POST',
                data : JSON.stringify(post_dict),
            };

            return ajax_rs('/graph/diff-commit-vis', req_opts, on_success,
                    on_error);
        }

        /**
         * commit a diff_set
         */
        this.commit_diff__set = function(diff_set, on_success, on_error) {

            var post_dict = {
                'diff_set' : diff_set
            }

            var req_opts = {
                type : 'POST',
                data : JSON.stringify(post_dict),
            };

            return ajax_rs('/graph/diff-commit-set', req_opts, on_success,
                    on_error);
        }


		

	   /**
	    * TODO: temp saveFeedback
	    */
	   this.saveFeedback = function(data, on_success, on_error) {

	       var post_dict = data

	       // prep request
	       var req_opts = {
	           type : 'POST',
	            data : JSON.stringify(post_dict)
	       };

	       ajax_rs('/feedback/save', req_opts, on_success, on_error);
	   }


	   /**
	    * query rhizi repo
	    */
	   this.query = function(query, on_success, on_error) {
	   
	       var post_dict = {
	           'query' : query
	       }
	   
	       // prep request
	       var req_opts = {
	           type : 'POST',
	            data : JSON.stringify(post_dict)
	       };
	   
	       ajax_rs('/graph/query', req_opts, on_success, on_error);
	   }


        /**
         * clone rhizi repo
         */
        this.clone = function(depth, on_success, on_error) {


            // prep request
            var req_opts = {
                type : 'POST',
            };

            ajax_rs('/graph/clone', req_opts, on_success, on_error);
        }

        /**
         * load node-set by id attribute
         *
         * @param on_complete_cb
         *            will be called with the returned json data on successful
         *            invocation
         * @param on_error
         *            error callback
         */
        this.load_node_set = function(id_set, on_success, on_error) {
			
            // prep request data
            var post_dict = {
                'id_set' : id_set
            }

            // prep request
            var req_opts = {
                type : 'POST',
                data : JSON.stringify(post_dict),
            };
			console.log('load_node_set')
            return ajax_rs('/load/node-set-by-id', req_opts, on_success,
                    on_error);
        }

        /**
         * load link set by src / dst id
         */
        this.load_link_set = function(link_ptr_set, on_success, on_error) {

            // prep request data
            var post_dict = {
                'link_ptr_set' : link_ptr_set
            }

            // prep request
            var req_opts = {
                type : 'POST',
                data : JSON.stringify(post_dict),
            };

            return ajax_rs('/load/link-set/by_link_ptr_set', req_opts,
                    on_success, on_error);
        }

        /**
         * add a node set
         */
        this.add_node_set = function(n_set, on_success, on_error) {
            var topo_diff = new Topo_Diff();
            topo_diff.node_set_add = n_set;

            return this.topo_diff_commit(topo_diff, on_success, on_error);
        }

        /**
         * add a link set
         */
        this.add_link_set = function(l_set, on_success, on_error) {
            var topo_diff = new Topo_Diff();
            topo_diff.link_set_add = l_set;

            return this.topo_diff_commit(topo_diff);
        }

        /**
         * remove node set
         */
        this.remove_node_set = function() {
            var topo_diff = null;
            return this.topo_diff_commit(topo_diff);
        }

        /**
         * remove link set
         */
        this.remove_link_set = function() {
            var topo_diff = null;
            return this.topo_diff_commit(topo_diff);
        }

        /**
         * update node set
         */
        this.update_node_set = function(attr_diff, on_success, on_error) {
            return this.attr_diff_commit(attr_diff, on_success, on_error);
        }

        /**
         * update link set
         */
        this.update_link_set = function() {
            var attr_diff = null;
            return this.attr_diff_commit(null);
        }
    }

    return new RZ_API_Backend();
});
