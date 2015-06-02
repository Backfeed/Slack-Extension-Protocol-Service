define(['jquery', 'jquery-ui', 'view/helpers', 'view/internal','rz_api_backend'],
function($, _unused_jquery_ui,  view_helpers, internal,rz_api_backend) {

var sliderObj = null;
var currentD = null,
    save_callback = function() {},
    delete_callback = function() {},
    keyup_callback = function() {};



/*
function _get_form_data() {
    return {
        name: $('.info #editformname').text(),
        type: $('.info #edittype').val(),
        url: $('.info #editurl').val(),
        status: $('.info #editstatus').val(),
        startdate: $("#editstartdate").val(),
        enddate: $("#editenddate").val(),
        description: $("#editdescription").text(),
    };
}
*/


function _get_form_data() {
    return {
        targetId: currentD.id,
		targetName: currentD.name,
		targetType: currentD.type,
        feedback: (''+sliderObj.slider( "option", "value" )),
        description: $("#editdescription").val(),
		
    };
}


function RGBChange() {
	$('#RGB').css('background', 'rgb(128,'+ Math.round( (sliderObj.slider( "option", "value" )-(-50))*2.4 )   +',128)');
};






		
//$('#edit-node-dialog__delete').click(function(e) {
//    e.preventDefault();
// 	hide();
//    return delete_callback(e, _get_form_data());
//});

//$('#edit-node-dialog__save').click(function(e) {	
//    e.preventDefault();
//    return save_callback(e, _get_form_data());
//});




function onSuccess(data) {
	// TBD: formely update node - and implement proper backend call and instead of changing here (before), change this only After success of backend ...
	currentD.feedback =sliderObj.slider( "option", "value" );
	currentD.description = $("#editdescription").val();
	currentD.avgFeedback = data['avgFeedback']
	console.log('saveFeedback succeeded. currentD:');
	console.dir(currentD);
}



$('.info').keyup(function(e) {
    return keyup_callback(e, _get_form_data());
});

function show(d) {
	console.log('showing element:');
   // try and connect to composy, the listener has to be loaded first in the anchor on doc ready:
   window.postMessage({ type: "NodeClicked", node: d }, "*");
	
	
	console.dir(d);
	currentD = d;
	
	
	console.log('initing  slider obj in show:');
	init();

	
	
    var info = $('.info'),
        f = false,
        t = true,
        visible = {
          "third-internship-proposal":  [t, t, t, t, f],
          "chainlink":                  [f, f, f, t, f],
          "skill":                      [f, f, f, t, t],
          "interest":                   [f, f, f, t, t],
          "_defaults":                  [f, f, f, t, t],
        },
        fields = ["#status", "#startdate", "#enddate", "#description", "#url"],
        flags = visible.hasOwnProperty(d.type) ? visible[d.type] : visible._defaults,
        i;

    internal.edit_tab.show('node');

    for (i = 0 ; i < flags.length; ++i) {
        var elem = info.find(fields[i]);
        elem[flags[i] ? 'show' : 'hide']();
    }

    $('.info').attr('class', 'info');
    $('.info').addClass('type-' + d.type); // Add a class to distinguish types for css

    $('.info').find('#editformname').text(d.name);
    $("#editenddate").datepicker({
      inline: true,
      showOtherMonths: true,
      dayNamesMin: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
    });
    $("#editstartdate").datepicker({
      inline: true,
      showOtherMonths: true,
      dayNamesMin: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
    });

    $('#editdescription').val(d.description);
    $('#edittype').val(d.type);
    $('#editurl').val(d.url);
    $('#editstatus').val(d.status);

    if (d.type === "third-internship-proposal") {
      $('#editstartdate').val(d.start);
      $('#editenddate').val(d.end);
    }


	// set feedback:
	if(d.feedback ){
		sliderObj.slider( "option", "value", d.feedback );
		RGBChange();
	}
	else{
		
		sliderObj.slider( "option", "value",0 );
		$('#RGB').css('background', 'grey');
	}
	

}

function init() {
	// TBD: create init method (BUG)
	
	sliderObj = $('#slider');
	sliderObj.slider({
	  slide: RGBChange,
		min: -50,
		max:50
	});
	
	
	$('#edit-node-dialog__delete').click(function(e) {
	    e.preventDefault();
		var data = _get_form_data();
		data['delete'] =  true;
	    rz_api_backend.saveFeedback(data, onSuccess);
		hide();
	});

	$('#edit-node-dialog__save').click(function(e) {
	    e.preventDefault();
		var data = _get_form_data();
		data['delete'] =  false;
	    rz_api_backend.saveFeedback(data, onSuccess);
		hide();
	});
	
}

function hide() {
    internal.edit_tab.hide();
}

function on_save(f) {
    save_callback = f;
}

function on_delete(f) {
    delete_callback = f;
}

function on_keyup(f) {
    keyup_callback = f;
}

return {
	init:init,
    show: show,
    hide: hide,
    isOpenProperty: internal.edit_tab.isOpenProperty,
    on_save: on_save,
    on_delete: on_delete,
    on_keyup: on_keyup,
};

});
