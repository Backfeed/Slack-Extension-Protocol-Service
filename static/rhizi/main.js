define(['textanalysis.ui', 'textanalysis', 'buttons', 'history', 'drag_n_drop', 'robot', 'model/core', 'rz_config', 'rz_core', 'view/selection', 'util', 'view/search', 'view/filter', 'feedback','view/node_info'],
function(textanalysis_ui,   textanalysis,   buttons,   history,   drag_n_drop,   robot,   model_core,   rz_config,   rz_core,        selection,   util,   search, filter, feedback,node_info) {

    function expand(obj){
        if (!obj.savesize) {
            obj.savesize = obj.size;
        }
        obj.size = Math.max(obj.savesize, obj.value.length);
    }

    this.main = function() {
        var json;

        console.log('Rhizi main started');
        $('#editname').onkeyup = function() { expand(this); };
        $('#editlinkname').onkeyup = function() { expand(this); };
        $('#textanalyser').onkeyup = function() { expand(this); };

        textanalysis_ui.main();

        json = util.getParameterByName('json');
        console.log('main json:'+json);

        if (json) {
	        console.log('recieved: Json: '+json);
	
            rz_core.load_from_json(json);
        }
        if (util.getParameterByName('debug')) {
            $(document.body).addClass('debug');
            rz_core.edit_graph.set_user('fakeuser');
            rz_core.main_graph.set_user('fakeuser');
            drag_n_drop.init();
        } else {
            drag_n_drop.prevent_default_drop_behavior();
        }

        document.body.onkeyup = function(e) {
            var key = (e.key || (e.charCode && String.fromCharCode(e.charCode))
                             || (e.which && String.fromCharCode(e.which))).toLowerCase();

            if (e.altKey && e.ctrlKey && key == 'i') {
                $('#textanalyser').focus();
            }
            if (e.altKey && e.ctrlKey && key == 'o') {
                search.focus();
            }
            if (e.ctrlKey && key == 'z' && e.target.nodeName !== 'INPUT') {
                // TODO: rz_core.main_graph.undo();
            }
        };

        var intro_task_elem = $('#intro-task');
        // TODO: messages (why tasks?) - this one is special but we want them to be handled in their own file.
        if (!localStorage.intro_task_hide) {
            intro_task_elem.show();
        }
        $('#intro-task .task-close-button').click(function(e) {
            localStorage.intro_task_hide = true;
            intro_task_elem.hide();
        });

        // TODO: interaction between the hack above and this
        model_core.init(rz_config);
        textanalysis.init(rz_core.main_graph);
        search.init();
		filter.init();
		
        //$.feedback({ajaxURL: rz_config.feedback_url});

    }

	this.push = function(input) {
		
		rz_core.push(input)
	}
	
	this.reset = function() {
		
		rz_core.reset()
	}
	
    return {
		reset:reset,
		push:push,
        main: main };
    }
);
