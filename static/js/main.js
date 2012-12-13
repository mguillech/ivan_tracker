function _create_option(value, html) {
    var option = $('<option/>');
    option.val(value);
    option.html(html);
    return option;
}

function _append_user(select, obj) {
    for (i = 0; i < obj.length; i++) {
        full_name = obj[i].fields.first_name + ' ' + obj[i].fields.last_name;
        option = _create_option(obj[i].pk, full_name);
        select.append(option);
    }
}

function _append_activity(select, obj) {
    for (i = 0; i < obj.length; i++) {
        name = obj[i].fields.name;
        option = _create_option(obj[i].pk, name);
        select.append(option);
    }
}

$('#create-event-btn').bind('click', function() {
    $.ajax({
        url: '/tracker/get-create-data/',
        method: 'POST',
        success: function(data) {
            $('.loading.create-event').hide();
            var trainees = $.parseJSON(data.trainees);
            var activities = $.parseJSON(data.activities);
            $('#add-trainee').empty();
            $('#add-activity').empty();
            _append_user($('#add-trainee'), trainees);
            _append_activity($('#add-activity'), activities);
        }
    });
    $('input[type=text]').val('');
});

$('.datepair input.time.start').on('changeTime', function() {
    var start_time_input = $(this);
    var start_time = start_time_input.val();
    var end_input = start_time_input.siblings('input.time.end');
    end_input.timepicker('option', 'minTime', start_time);
    end_input.timepicker('option', 'maxTime', '11:30pm');
});

$('#create-event').bind('click', function() {
    return $('#create-event-form').submit();
});

$('#create-event-form').bind('ajaxSubmit', function() {
   form = $(this);
   csrftoken = $('input[name=csrfmiddlewaretoken]').val();
   data = JSON.stringify(form.serializeArray().slice(1));
   tz_offset = new Date().getTimezoneOffset() / -60;
   $.ajax({
      url: form.attr('action'),
      type: form.attr('method'),
      data: {'csrfmiddlewaretoken': csrftoken, 'data': data, 'tz_offset': tz_offset},
      beforeSend: function () {
        $('.loading.create-event').show();
      },
      success: function(response) {
        $('.loading.create-event').hide();
        if (response.status != false) {
            $('#createModal').trigger('close');
            $('#calendar').fullCalendar('refetchEvents');
        } else {
            msg = response.msg;
            $('#create-event-alert').html(create_alert('Create event error!', msg));
        }
      }
   });
   return false;
});

$('input').change(function (e) {
    input = $(e.target || e.srcElement);
    nextfocus = input.attr('data-nextfocus');
    if (nextfocus)
        $(nextfocus).focus();
});

function create_alert(title, body) {
    alert_div = $('<div/>');
    alert_div.addClass("alert alert-block alert-error fade in");
    close_button = $('<button type="button"/>');
    close_button.addClass("close");
    close_button.attr('data-dismiss', "alert");
    close_button.html('&times');
    alert_heading = $('<h4/>');
    alert_heading.addClass("alert-heading");
    alert_heading.html(title);
    alert_body = $('<p/>');
    alert_body.addClass("alert-body");
    alert_body.html(body);
    alert_div.append(close_button);
    alert_div.append(alert_heading);
    alert_div.append(alert_body);
    return alert_div;
}

$('.modal').bind('close', function() {
    modal = $(this);
    modal.modal('hide');
});

$('#create-user').click(function() {
    return $('#create-user-form').submit();
});

$('#create-user-form').bind('ajaxSubmit', function() {
    form = $(this);
    csrftoken = $('input[name=csrfmiddlewaretoken]').val();
    data = JSON.stringify(form.serializeArray().slice(1));
    group = $('input[name=group]').val();
    $.ajax({
        url: form.attr('action'),
        type: form.attr('method'),
        data: {'csrfmiddlewaretoken': csrftoken, 'data': data},
        beforeSend: function() {
            $('.loading.create-user').show();
        },
        success: function(response) {
            $('.loading.create-user').hide();
            if (response.status != false) {
                $('#createModal').trigger('close');
                get_data('#' + group + 's', group + 's');
            } else {
                msg = response.msg;
                $('#create-user-alert').html(create_alert('Create user error!', msg));
            }
        }
    });
    return false;
});

function get_data(div, data_group, callback) {
    loading = $('.loading.show-' + data_group + 's');
    $.ajax({
        url: '/tracker/get-' + data_group + '/',
        beforeSend: function() {
            loading.show();
        },
        success: function(response) {
            loading.hide();
            $(div).html(response);
            if (callback)
                callback();
        }
    });
}

$('#create-activity').click(function() {
    $('#create-activity-form').submit();
});

$('#create-activity-form').bind('ajaxSubmit', function() {
    form = $(this);
    csrftoken = $('input[name=csrfmiddlewaretoken]').val();
    data = JSON.stringify(form.serializeArray().slice(1));
    $.ajax({
        url: form.attr('action'),
        type: form.attr('method'),
        data: {'csrfmiddlewaretoken': csrftoken, 'data': data},
        beforeSend: function() {
            $('.loading.create-activity').show();
        },
        success: function(response) {
            $('.loading.create-activity').hide();
            if (response.status != false) {
                $('#createModal').trigger('close');
                get_data('#activities', 'activities');
            } else {
                msg = response.msg;
                $('#create-activity-alert').html(create_alert('Create activity error!', msg));
            }
        }
    });
    return false;
});

$('#download-report-btn').bind('click', function() {
   window.location.href = '/tracker/report-download/';
});

function formatDate(dt) {
    y = dt.getFullYear();
    m = zeroPad(dt.getMonth() + 1);
    d = zeroPad(dt.getDate());
    h = zeroPad(dt.getHours());
    M = zeroPad(dt.getMinutes());
    s = zeroPad(dt.getSeconds());
    return m + '/' + d + '/' + y + ' ' + h + ':' + M + ':' + s
}

function zeroPad(n) {
    return (n < 10 ? '0' : '') + n;
}

function convert_datetimes() {
    $('.timestamp').each(function() {
        var elem = $(this);
        var val = elem.text();
        var dt = new Date(val * 1000);
        elem.text(formatDate(dt));
    });
}

function negativeEvent(value, element) {
    var parent = $(element).parent('p');
    var sd = parent.find('input.start.date');
    var ed = parent.find('input.end.date');
    var st = parent.find('input.start.time');

    if (sd.val() == ed.val()) {
        return !($(element).timepicker('getSecondsFromMidnight') < st.timepicker('getSecondsFromMidnight'));
    }
    return true;
}

function editEventModal(event, callback) {
    $('#editModal').modal();
    $.ajax({
        url: '/tracker/get-create-data/',
        method: 'POST',
        success: function(data) {
            $('.loading.edit-event').hide();
            var trainees = $.parseJSON(data.trainees);
            var activities = $.parseJSON(data.activities);
            $('#edit-trainee').empty();
            $('#edit-activity').empty();
            _append_user($('#edit-trainee'), trainees);
            _append_activity($('#edit-activity'), activities);
            callback(event);
        }
    });
    $('input[type=text]').val('');
}

function updateEvent(event) {
    $.ajax({
        url: '/tracker/get-event/' + event.id + '/',
        method: 'POST',
        success: function(data) {
            $('#edit-trainee').find('option[value=' + data.trainee + ']').attr('selected', 'selected');
            $('#edit-activity').find('option[value=' + data.activity + ']').attr('selected', 'selected');
            $('#edit-start-date').datepicker('setDate', new Date(data.start * 1000));
            $('#edit-start-time').timepicker('setTime', new Date(data.start * 1000));
            $('#edit-end-date').datepicker('setDate', new Date(data.end * 1000));
            $('#edit-end-time').timepicker('setTime', new Date(data.end * 1000));
            $('#edit-comment').val(data.comment);
            $('#event-pk').val(data.id);
        }
    });
}

$('#edit-event').bind('click', function() {
    return $('#edit-event-form').submit();
});

$('#edit-event-form').bind('ajaxSubmit', function() {
    form = $(this);
    csrftoken = $('input[name=csrfmiddlewaretoken]').val();
    data = JSON.stringify(form.serializeArray().slice(1));
    tz_offset = new Date().getTimezoneOffset() / -60;
    $.ajax({
        url: form.attr('action'),
        type: form.attr('method'),
        data: {'csrfmiddlewaretoken': csrftoken, 'data': data, 'tz_offset': tz_offset},
        beforeSend: function () {
            $('.loading.edit-event').show();
        },
        success: function(response) {
            $('.loading.edit-event').hide();
            if (response.status != false) {
                $('#editModal').trigger('close');
                $('#calendar').fullCalendar('refetchEvents');
            } else {
                msg = response.msg;
                $('#edit-event-alert').html(create_alert('Edit event error!', msg));
            }
        }
    });
    return false;
});

function setupUserHandler() {
    $('.edit-user').bind('click', function() {
        $('#editModal').modal();
        var user_pk = $(this).attr('data-pk');
        var group = $(this).attr('data-group');
        $.ajax({
            url: '/tracker/get-user/' + user_pk + '/',
            method: 'POST',
            beforeSend: function () {
                $('.loading.edit-user').show();
            },
            success: function(data) {
                $('.loading.edit-user').hide();
                var edit_form = $('#edit-user-form');
                edit_form.find('#id_username').val(data.username);
                edit_form.find('#id_password').removeAttr('required minlength');
                edit_form.find('#id_first_name').val(data.first_name);
                edit_form.find('#id_last_name').val(data.last_name);
                edit_form.find('#id_email').val(data.email);
                edit_form.find('#user-pk').val(data.pk);
                edit_form.find('#group').val(data.group);
                if (data.group.toLowerCase() == 'trainee')
                    edit_form.find('#trainer-cost').hide();
                else
                    edit_form.find('#edit-cost').val(data.cost);
            }
        });
    });

    $('#delete-user').bind('click', function() {
        confirmed = confirm('Are you sure that you want to delete this user?');
        if (confirmed) {
            var edit_form = $('#edit-user-form');
            var user_pk = edit_form.find('#user-pk').val();
            var group = edit_form.find('#group').val().toLowerCase();
            $.ajax({
                url: '/tracker/delete-user/' + user_pk + '/',
                beforeSend: function () {
                    $('.loading.edit-user').show();
                },
                success: function(data) {
                    $('.loading.edit-user').hide();
                    $('#editModal').trigger('close');
                    get_data('#' + group + 's', group + 's');
                }
            });
        }
    });
}

$('#edit-user').bind('click', function() {
    return $('#edit-user-form').submit();
});

$('#edit-user-form').bind('ajaxSubmit', function() {
    form = $(this);
    csrftoken = $('input[name=csrfmiddlewaretoken]').val();
    data = JSON.stringify(form.serializeArray().slice(1));
    group = $('#edit-user-form').find('#group').val().toLowerCase();
    $.ajax({
        url: form.attr('action'),
        type: form.attr('method'),
        data: {'csrfmiddlewaretoken': csrftoken, 'data': data},
        beforeSend: function () {
            $('.loading.edit-user').show();
        },
        success: function(response) {
            $('.loading.edit-user').hide();
            if (response.status != false) {
                $('#editModal').trigger('close');
                get_data('#' + group + 's', group + 's');
            } else {
                msg = response.msg;
                $('#edit-user-alert').html(create_alert('Edit user error!', msg));
            }
        }
    });
    return false;
});