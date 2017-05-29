$(document).ready(function() {

    function addDays(date, days) {
	var result = new Date(date);
	result.setDate(result.getDate() + days);
	return result;
    }

    function removeDays(date, days) {
        var result = new Date(date);
        result.setDate(result.getDate() - days);
        return result;
    }

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
	var startdate = addDays($(this).datepicker('getDate'), 1);
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
	var enddate = removeDays($(this).datepicker('getDate'), 1);
	$('#form-field-startdate').datepicker(
	    'setEndDate', enddate);
    });

});
