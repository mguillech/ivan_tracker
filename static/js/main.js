function _create_option(value, html) {
    var option = $('<option/>');
    option.attr('value', value);
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
    $('#create-modal').modal();
    $.ajax({
        url: '/tracker/get-create-data/',
        method: 'POST',
        success: function(data) {
            $('.loading.create-event').hide();
            var trainees = $.parseJSON(data.trainees);
            var activities = $.parseJSON(data.activities);
            $('#trainee').empty();
            $('#activity').empty();
            _append_user($('#trainee'), trainees);
            _append_activity($('#activity'), activities);
        }
    });
    $('input[type=text]').val('');
});

$('.datepair input.time.start').on('changeTime', function() {
    var start_time = $('.datepair input.time.start').val();
    var end_input = $('.datepair input.time.end');
    end_input.timepicker('option', 'minTime', start_time);
});

$('#create-event').click(function() {
    $('#create-event-form').submit();
});

$('#create-event-form').submit(function() {
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
        nextfocus_elem = $('input' + nextfocus).focus();
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
    $('#create-user-form').submit();
});

$('#create-user-form').submit(function() {
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

$('#create-activity-form').submit(function() {
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