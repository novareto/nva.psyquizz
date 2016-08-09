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

});

function dataURItoBlob(dataURI) {
    // convert base64/URLEncoded data component to raw binary data held in a string
    var byteString;
    if (dataURI.split(',')[0].indexOf('base64') >= 0)
        byteString = atob(dataURI.split(',')[1]);
    else
        byteString = unescape(dataURI.split(',')[1]);

    // separate out the mime component
    var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];

    // write the bytes of the string to a typed array
    var ia = new Uint8Array(byteString.length);
    for (var i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }

    return new Blob([ia], {type:mimeString});
}
