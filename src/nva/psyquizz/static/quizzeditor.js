$( document ).ready(function() {
    $('form[id!="CreateCourse"] #form-field-about').summernote({
        height: 300,
        toolbar: [
            ['style', ['bold', 'underline']],
        ]
    });

    $('form[id!="CreateCourse"] #form-field-text').summernote({
        height: 300,
        toolbar: [
            ['style', ['bold', 'underline']],
        ]
    });

    $('form#CreateCourse #form-field-about').summernote({
        height: 300,
    });

    $('form#CreateCourse #form-field-text').summernote({
        height: 300,
    });

    $('#form-field-form-field-criterias :input').prop('checked', 'true')
});
