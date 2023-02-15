$(document).ready(function() {
    var button = $('input[type=submit][name="form.action.add"]');
    var conditions = $('input[type=radio][name="form.field.accept"]');

    var e = $("<p></p>");
    $("#field-form-field-accept").append(e)
    e.hide()
    e.html("<p>Der Fragebogen FGBU steht nur den Mitgliedsbetrieb der BG RCI(VBG/ BG ETEM) über unser Online-Tool zur Verfügung. Wenn Ihr Unternehmen nicht bei der BG RCI (VBG/ BG ETEM)  versichert ist, wenden Sie sich bitte an Ihren zuständige Unfallversicherungsträger und prüfen Sie die dortigen Angebote zur Gefährdungsbeurteilung psychischer Belastung.</p><p>Eine gewerbliche Nutzung von PsyBel Befragung und des dort eingesetzten FGBU Fragebogens sowie dessen Weiterverbreitung ist ohne Rücksprache mit den Autoren des Fragebogens nicht gestattet</p>");

    if ($('input:radio[name="form.field.accept"][value=ja]').is(':checked')) {
        button.prop('disabled', false);
        e.hide();
    } else {
        button.prop('disabled', true);
        if ($('input:radio[name="form.field.accept"][value=nein]').is(':checked')) {
            e.fadeIn();
        }
    }
    conditions.on('change', function() {
        if ($(this).val() != 'ja') {
            button.prop('disabled', true);
            e.fadeIn();
        } else {
            button.prop('disabled', false);
            e.hide();
        }
    })
})
