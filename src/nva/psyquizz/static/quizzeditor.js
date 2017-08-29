$( document ).ready(function() {
    $('form[id!="CreateCourse"] #form-field-about').summernote({
        height: 400,
         styleWithSpan: false,
        toolbar: [
            ['style', ['bold', 'underline']],
        ]
    });

    $('form[id!="CreateCourse"] #form-field-text').summernote({
        height: 400,
         styleWithSpan: false,
        toolbar: [
            ['style', ['bold', 'underline']],
        ]
    });

    $('form#CreateCourse #form-field-about').summernote({
        height: 400,
    });

    $('form#CreateCourse #form-field-text').summernote({
        height: 400,
    });

    $('#form-field-form-field-criterias :input').prop('checked', 'true')
});
