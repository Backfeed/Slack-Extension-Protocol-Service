"use strict"

define(['jquery','view/node_info', 'view/edge_info', 'view/internal','jquery-ui'],
function($,view_node_info,   view_edge_info,   view_internal,__jqueryui) {

	function init() {
		console.log('filter: init.');
		
		//$("#example").multiselect({header:false,selectedList:5});
	   
	
		$('#feedback-check').click(function() {
		    var $this = $(this);
		    // $this will contain a reference to the checkbox   
		    if ($this.is(':checked')) {
				console.log('checked feedback');
		        // the checkbox was checked 
		    } else {
		        // the checkbox was unchecked
				console.log('un checked feedback');
		    }
		});

    };


return {
    
    'init': init,
}
});