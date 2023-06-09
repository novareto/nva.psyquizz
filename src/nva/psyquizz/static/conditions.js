$(document).ready(function() {
    var button = $('input[type=submit][name="form.action.add"]');
    var conditions = $('input[type=radio][name="form.field.accept"]');

    let e = $("<p></p>");
    $("#field-form-field-accept").append(e)
    e.hide()
    e.html("<p>Der Fragebogen FGBU steht nur den Mitgliedsbetrieb der Berufsgenossenschaft über unser Online-Tool zur Verfügung. Wenn Ihr Unternehmen nicht bei uns  versichert ist, wenden Sie sich bitte an Ihren zuständige Unfallversicherungsträger und prüfen Sie die dortigen Angebote zur Gefährdungsbeurteilung psychischer Belastung.</p><p>Eine gewerbliche Nutzung des Online-Tools und des dort eingesetzten FGBU Fragebogens sowie dessen Weiterverbreitung ist ohne Rücksprache mit den Autoren des Fragebogens nicht gestattet</p>");

    let f = $("<p></p>");
    $("#field-form-field-accept").append(f)
    f.hide()
    f.html("<p>Hiermit versichere ich, dass mein Unternehmen Mitglied der Berufsgenossenschaft ist. Das Befragungsinstrument wird nur zu internen betrieblichen Zwecken eingesetzt.</p>");

    if ($('input:radio[name="form.field.accept"][value=ja]').is(':checked')) {
        button.prop('disabled', false);
        e.hide();
        f.show();
    } else {
        button.prop('disabled', true);
        if ($('input:radio[name="form.field.accept"][value=nein]').is(':checked')) {
            e.show();
            f.hide()
        }
    }
    conditions.on('change', function() {
        if ($(this).val() != 'ja') {
            button.prop('disabled', true);
            f.hide();
            e.show();
        } else {
            button.prop('disabled', false);
            e.hide();
            f.show();
        }
    })
})
