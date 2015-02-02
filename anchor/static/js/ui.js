
$('.scrollup').click(function(){
    $('html, body').animate({ scrollTop: 0 }, 600);
    return false;
});

function show_message(message, alert_class) {
    $('#generated_messages').html(
        '<div class="alert alert-' + alert_class + '">' +
        '<button type="button" class="close" data-dismiss="alert">' +
        '&times;</button><p>' + message + '</p></div>');
}

$('body').on('hidden.bs.modal', '.modal', function () {
    $(this).removeData();
});

function change_to_loading_button(class_name, text) {
    var loading_html = text + ' <i class="fa fa-spinner fa-spin"></i>';
    $('.' + class_name)
        .html(loading_html)
        .removeClass('btn-info')
        .addClass('btn-warning');
}

function reset_button_state(class_name, text) {
    $('.' + class_name)
        .html(text)
        .removeClass('btn-warning')
        .addClass('btn-info');
}

function change_button_text(class_name, text, add_class, remove_class) {
    var loading_html = text;
    $('.' + class_name)
        .html(loading_html)
        .removeClass('btn-' + remove_class)
        .addClass('btn-' + add_class);
}
