$( document ).ready(function() {
    $('div#field-came_from').hide();
    $('div#form-field-activation').hide(); 
    $('div.breadcrumb').hide();
    $('div#field-activation').hide(); 
    $('span.field-required').hide();

    $('.panel').on('hidden.bs.collapse', function (e) {
	sessionStorage.removeItem("accordion");
    })

    $('.panel').on('show.bs.collapse', function (e) {
	var panel = $(this).children('.panel-collapse').attr('id');
	sessionStorage.setItem("accordion", panel);
    })

    var panel = sessionStorage.getItem("accordion");
    if (panel == null) {
	var accordion = $(".panel-collapse").first();
	accordion.addClass('in');
	accordion.prev('.panel-heading').children('a').removeClass('collapsed');
    } else {
	var accordion = $('#' + sessionStorage.getItem("accordion"));
	accordion.addClass('in');
	accordion.prev('.panel-heading').children('a').removeClass('collapsed');
    }

    $('input[type=checkbox]').change(function() {
	$("#form-action-filter").click();
    });

    $('#form-field-form-field-employees, #form-field-form-field-type').hide();
    $('#form-field-exp_db').change( function(event){
       $('#form-field-form-field-employees, #form-field-form-field-type').toggle();
    });

    $("a[href='https://www.bgetem.de/arbeitssicherheit-gesundheitsschutz/themen-von-a-z-1/psychische-belastung-und-beanspruchung/gemeinsam-zu-gesunden-arbeitsbedingungen-beurteilung-psychischer-belastung']").attr('target','_blank');
    $("a[href='http://www.bgetem.de/die-bgetem/impressum']").attr('target','_blank');


    $('div#form-field-form-field-nb_students').hide();

    $('div#form-field-form-field-strategy input:radio').click(function() {
        value = $(this).val()
        if (value == 'fixed') {
            $('div#form-field-form-field-nb_students').fadeIn();
        }
        if (value == 'mixed') {
            $('div#form-field-form-field-nb_students').fadeIn();
        }
        if (value == 'free') {
            $('div#form-field-form-field-nb_students').fadeOut();
        }
    }
    )

    function validate_date(startDate, endDate) {
        var regExp = /(\d{1,2})\/(\d{1,2})\/(\d{2,4})/;
        if(parseInt(endDate.replace(regExp, "$3$2$1")) > parseInt(startDate.replace(regExp, "$3$2$1"))) {
	    return false;
        }
        return true;
    }

    function check_date() {
        enddate = $('#form-field-enddate').val();
        startdate = $('#form-field-startdate').val();
        correct = validate_date(startdate, enddate);
        if (correct == false) {
            alert('The end date needs to be greater than the start date');
            $('#form-field-enddate').val(startdate);
        }
    }

    //$('#form-field-startdate').on('changeDate', function() {
//	check_date();
 //   })

   // $('#form-field-enddate').on('changeDate', function() {
    //    check_date();
    //})

});
