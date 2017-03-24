$(document).ready(function() {

    // set default dates
    var start = new Date();

    // set end date to max one year period:
    var end = new Date();
    end.setDate(end.getDate() + 365); 
    
    $('#form-field-startdate').datepicker({
	format: 'dd/mm/yyyy',
	orientation: 'right',
	language: 'de',
	startDate: start,
	endDate: end
    }).on('changeDate', function() {
	// set the start to not be later than the end:
	var startdate = new Date($(this).datepicker('getDate'));
	$('#form-field-enddate').datepicker(
	    'setStartDate', startdate);
    }); 

    $('#form-field-enddate').datepicker({
	format: 'dd/mm/yyyy',
	orientation: 'right',
	language: 'de',
	startDate : start,
	endDate   : end
    }).on('changeDate', function() {
	// set the end to not be later than the start:
	var enddate = new Date($(this).datepicker('getDate'));
	$('#form-field-startdate').datepicker(
	    'setEndDate', enddate);
    });

});
