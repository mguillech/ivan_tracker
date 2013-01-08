import json
import datetime
import random
import xlwt
from operator import itemgetter
from dateutil import parser as dateutil_parser
from django.contrib.auth import login as login_function, logout as logout_function, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import logout_then_login
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.utils.timezone import utc
from django.core.serializers import serialize
from django.views.generic import ListView
from tracker.forms import UserForm, ActivityForm

from tracker.models import TimesheetEntry, Activity, UserProfile
from tracker.utils import to_timestamp

def user_view(request, group):
    form = UserForm()
    return render_to_response('tracker/user.html', {'form': form, 'group': group},
        context_instance=RequestContext(request))


class TrainerView(ListView):
        queryset = UserProfile.objects.filter(group='Trainer')
        context_object_name = 'trainer_list'
        template_name = 'tracker/parts/trainers_part.html'

        @method_decorator(login_required)
        def dispatch(self, *args, **kwargs):
            return super(TrainerView, self).dispatch(*args, **kwargs)


class TraineeView(ListView):
    queryset = UserProfile.objects.filter(group='Trainee')
    context_object_name = 'trainee_list'
    template_name = 'tracker/parts/trainees_part.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TraineeView, self).dispatch(*args, **kwargs)


@login_required
def home(request):
    group = request.user.get_profile().group or 'Admin'
    return render_to_response('tracker/home_%s.html' % group.lower(), {'group': group},
        context_instance=RequestContext(request))

def login(request):
    msg = u''
    if request.user and request.user.is_authenticated():
        return redirect(reverse('home'))

    if request.REQUEST.has_key('next') and request.REQUEST['next']:
        next_url = request.REQUEST['next']
    else:
        next_url = reverse('home')
    username, password = request.POST.get('username'), request.POST.get('password')
    if username and password:
        user = authenticate(username=username, password=password)
        if user:
            login_function(request, user)
            return redirect(next_url)
        else:
            msg = u'Invalid username/password'
    return render_to_response('tracker/login.html', {'msg': msg}, context_instance=RequestContext(request))

def logout(request):
    if request.user and request.user.is_authenticated:
        return logout_then_login(request)
    else:
        return redirect(reverse('login'))

@login_required
def get_events(request):
    start, end = request.GET.get('start'), request.GET.get('end')
    group = request.user.get_profile().group
    if group == 'Admin':
        kwargs = {}
    else:
        kwargs = {group.lower(): request.user.get_full_name()}
    if start:
        start = datetime.datetime.fromtimestamp(float(start), utc)
    if end:
        end = datetime.datetime.fromtimestamp(float(end), utc)
    kwargs.update({'start__gte': start, 'end__lte': end})
    entries = [ {'id': entry.pk, 'title': unicode(entry), 'allDay': False, 'start': to_timestamp(entry.start),
                 'end': to_timestamp(entry.end),
                 'color': 'rgb%s' % UserProfile.objects.get(user__first_name=entry.trainer.split()[0],
                     user__last_name=entry.trainer.split()[1]).color }
                for entry in TimesheetEntry.objects.filter(**kwargs) ]
    return HttpResponse(json.dumps(entries), content_type='application/json')

@login_required
def get_event(request, pk):
    event = get_object_or_404(TimesheetEntry, pk=pk)
    start = to_timestamp(event.start)
    end = to_timestamp(event.end)
    trainer = User.objects.get(first_name=event.trainer.split()[0], last_name=event.trainer.split()[1])
    trainee = User.objects.get(first_name=event.trainee.split()[0], last_name=event.trainee.split()[1])
    info = {'id': pk, 'title': unicode(event), 'trainer': trainer.pk, 'trainee': trainee.pk,
            'activity': event.activity.pk, 'start': start, 'end': end, 'comment': event.comment }
    return HttpResponse(json.dumps(info), content_type='application/json')

@login_required
def add_event(request):
    def _add_entry():
        TimesheetEntry.objects.create(trainer=trainer.get_full_name(), trainee=trainee.get_full_name(),
            trainer_cost=trainer.get_profile().cost, activity=activity, start=start, end=end, comment=comment)

    def _check_end(should_return=True):
        if TimesheetEntry.objects.filter(Q(start__range=(start, end)) | Q(end__range=(start, end)),
            trainer=trainer.get_full_name()):
            if should_return:
                return HttpResponse(json.dumps({'status': False,
                        'msg': 'Start or end date/time overlaps an existing event. Try setting other dates/times.'}),
                    content_type='application/json')
            return should_return

    data = request.POST.get('data')
    tz_offset = request.POST.get('tz_offset')
    if data and tz_offset:
        data = json.loads(data)
        input_getter = itemgetter('name', 'value')
        create = dict(input_getter(i) for i in data)
        trainer = request.user
        trainee = User.objects.get(pk=create['trainee'])
        activity = Activity.objects.get(pk=create['activity'])
        start = original_start = dateutil_parser.parse('%s %s %s' % (create['start-date'], create['start-time'],
                                                    tz_offset)).astimezone(utc)
        end = original_end = dateutil_parser.parse('%s %s %s' % (create['end-date'], create['end-time'],
                                                  tz_offset)).astimezone(utc)
        repeat = create.get('repeat')
        comment = create['comment']
        msg = 'Event(s) created successfully.'
        _check_end()
        _add_entry()
        if repeat:
            if not repeat.isdigit():
                return HttpResponse(json.dumps({'status': False, 'msg': 'Supplied number of weeks is invalid.'}),
                    content_type='application/json')
            repeat = int(repeat)
            days = [ i for i in xrange(7, repeat * 7 + 1,  7) ]
            for day in days:
                start = original_start + datetime.timedelta(days=day)
                end = original_end + datetime.timedelta(days=day)
                if _check_end(False) is False:
                    msg += ' However, one of the events overlapped an existing one and it could not be created again.'
                _add_entry()
        return HttpResponse(json.dumps({'status': True, 'msg': msg}),
            content_type='application/json')
    else:
        return HttpResponseBadRequest

@login_required
def update_event(request):
    profile = request.user.get_profile()
    data = request.POST.get('data')
    tz_offset = request.POST.get('tz_offset')
    if data and tz_offset:
        data = json.loads(data)
        input_getter = itemgetter('name', 'value')
        edit = dict(input_getter(i) for i in data)
        trainee = UserProfile.objects.get(pk=edit['trainee'])
        activity = Activity.objects.get(pk=edit['activity'])
        start = dateutil_parser.parse('%s %s %s' % (edit['start-date'], edit['start-time'],
                                                    tz_offset)).astimezone(utc)
        end = dateutil_parser.parse('%s %s %s' % (edit['end-date'], edit['end-time'], tz_offset)).astimezone(utc)
        comment = edit['comment']
        TimesheetEntry.objects.filter(pk=edit['event-pk']).update(trainee=unicode(trainee),
            trainer_cost=profile.cost, activity=activity, start=start, end=end, comment=comment)
        return HttpResponse(json.dumps({'status': True, 'msg': 'Event successfully edited.'}),
            content_type='application/json')
    else:
        return HttpResponseBadRequest

@login_required
def get_create_data(request):
    if request.is_ajax():
        trainee_profiles = UserProfile.objects.filter(group='Trainee')
        trainees = serialize('json', [ p.user for p in trainee_profiles ], fields=('first_name', 'last_name'))
        activities = serialize('json', Activity.objects.all())
        return HttpResponse(json.dumps({'trainees': trainees, 'activities': activities}),
            content_type='application/json')
    else:
        return HttpResponseBadRequest

@login_required
def add_user(request):
    def _generate_color():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    data = request.POST.get('data')
    if data:
        data = json.loads(data)
        input_getter = itemgetter('name', 'value')
        create = dict(input_getter(i) for i in data)
        group = create.get('group')
        form = UserForm(create)
        if form.is_valid() and group:
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            cost = create.get('cost')
            user.save()
            profile = user.get_profile()
            profile.group = group.capitalize()
            if cost:    # Trainer
                profile.cost = cost
            profile.color = str(_generate_color())
            profile.save()
            status = True
            message = '%s successfully created.' % profile.group
        else:
            status = False
            message = 'There was an error while creating your %s user.' % group
        return HttpResponse(json.dumps({'status': status, 'msg': message}), content_type='application/json')
    else:
        return HttpResponseBadRequest()

@login_required
def get_user(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)
    user = profile.user
    info = {'pk': user.pk, 'username': user.username, 'first_name': user.first_name,
            'last_name': user.last_name, 'email': user.email,
            'group': profile.group}
    if profile.group.lower() == u'trainer':
        info.update({'cost': profile.cost})
    return HttpResponse(json.dumps(info), content_type='application/json')

@login_required
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    return HttpResponse(json.dumps({'status': True}), content_type='application/json')

@login_required
def update_user(request):
    data = request.POST.get('data')
    if data:
        data = json.loads(data)
        input_getter = itemgetter('name', 'value')
        edit = dict(input_getter(i) for i in data)
        user = get_object_or_404(User, pk=edit['user-pk'])
        profile = user.get_profile()
        form = UserForm(edit, instance=user)
        if 'password' in form.errors:
            form.errors.pop('password')
        if form.is_valid():
            user = form.save(commit=False)
            password = edit['password']
            if password != u'':
                user.set_password(password)
            user.save()
            cost = edit.get('cost')
            if cost and profile.group == 'Trainer':    # Trainer
                profile.cost = cost
            profile.save()
            status = True
            message = u'%s successfully updated.' % profile.group.capitalize()
        else:
            status = False
            message = u'There was an error while updating your %s user.' % profile.group
        return HttpResponse(json.dumps({'status': status, 'msg': message}), content_type='application/json')
    else:
        return HttpResponseBadRequest()

@login_required
def trainer_list(request):
    return user_view(request, 'Trainer')

@login_required
def trainee_list(request):
    return user_view(request, 'Trainee')

@login_required
def activity_list(request):
    form = ActivityForm()
    return render_to_response('tracker/activities.html', {'form': form}, context_instance=RequestContext(request))

@login_required
def activity_add(request):
    data = request.POST.get('data')
    if data:
        data = json.loads(data)
        input_getter = itemgetter('name', 'value')
        create = dict(input_getter(i) for i in data)
        form = ActivityForm(create)
        if form.is_valid():
            _ = form.save()
            status = True
            message = 'Activity successfully created.'
        else:
            status = False
            message = 'There was an error while creating your activity.'
        return HttpResponse(json.dumps({'status': status, 'msg': message}), content_type='application/json')
    else:
        return HttpResponseBadRequest()

@login_required
def report_download(request):
    book = xlwt.Workbook(encoding='utf8')
    sheet = book.add_sheet('Activity Report')
    default_style = xlwt.Style.default_style
    datetime_style = xlwt.easyxf(num_format_str='mm/dd/yyyy hh:mm:ss')
    date_style = xlwt.easyxf(num_format_str='mm/dd/yyyy')

    sheet.write(0, 0, u'ID', style=default_style)
    sheet.write(0, 1, u'Trainer', style=default_style)
    sheet.write(0, 2, u'Trainee', style=default_style)
    sheet.write(0, 3, u'Activity', style=default_style)
    sheet.write(0, 4, u'Start date/time (UTC)', style=default_style)
    sheet.write(0, 5, u'End date/time (UTC)', style=default_style)
    sheet.write(0, 6, u'Comments', style=default_style)
    sheet.write(0, 7, u'Trainer Cost per hour', style=default_style)
    sheet.write(0, 8, u'Total Activity Cost', style=default_style)
    values_list = TimesheetEntry.objects.all().values_list('id', 'trainer', 'trainee', 'activity', 'start', 'end',
        'comment')

    for row, rowdata in enumerate(values_list):
        trainer_cost = total_cost = 'NA'
        for col, val in enumerate(rowdata):
            if col == 0:
                entry = TimesheetEntry.objects.get(pk=val)
                trainer_cost = entry.hourly_cost or 'NA'
                total_cost = entry.total_cost or 'NA'
            if col == 3:
                val = unicode(Activity.objects.get(pk=val))
            if col == 6:
                val = entry.comment or 'No comments'
            if isinstance(val, datetime.datetime):
                style = datetime_style
                if val.tzinfo:
                    val = val.replace(tzinfo=None)
            elif isinstance(val, datetime.date):
                style = date_style
            else:
                style = default_style

            sheet.write(row + 1, col, val, style=style)
        sheet.write(row + 1, col + 1, trainer_cost, style=default_style)
        sheet.write(row + 1, col + 2, total_cost, style=default_style)

    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Activity_Report_%s.xls' % datetime.datetime.now().strftime(
                                                                                        '%Y%m%d%H%M%S')
    book.save(response)
    return response
