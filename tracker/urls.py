from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, TemplateView
from tracker.models import Activity, TimesheetEntry
from tracker.views import TrainerView, TraineeView

urlpatterns = patterns('tracker.views',
    url(r'^$', 'home'),
    url(r'^login/$', 'login', name='login'),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^get-events/$', 'get_events', name='get-events'),
    url(r'^get-event/(\d+)/$', 'get_event', name='get-event'),
    url(r'^add-event/$', 'add_event', name='add-event'),
    url(r'^update-event/$', 'update_event', name='update-event'),
    url(r'^get-create-data/$', 'get_create_data', name='get-create-data'),
    url(r'^add-user/$', 'add_user', name='add-user'),
    url(r'^get-user/(\d+)/$', 'get_user', name='get-user'),
    url(r'^delete-user/(\d+)/$', 'delete_user', name='delete-user'),
    url(r'^update-user/$', 'update_user', name='update-user'),
    url(r'^trainer/$', 'trainer_list', name='trainer-list'),
    url(r'^get-trainers/$', TrainerView.as_view(), name='get-trainers'),
    url(r'^trainee/$', 'trainee_list', name='trainee-list'),
    url(r'^get-trainees/$', TraineeView.as_view(), name='get-trainees'),
    url(r'^activity/$', 'activity_list', name='activity-list'),
    url(r'^get-activities/$', login_required(ListView.as_view(model=Activity, context_object_name='activity_list',
        template_name='tracker/parts/activities_part.html')), name='get-activities'),
    url(r'^category/add/$', 'category_add', name='add-category'),
    url(r'^activity/add/$', 'activity_add', name='add-activity'),
    url(r'^report/$', login_required(TemplateView.as_view(template_name='tracker/report.html')), name='report'),
    url(r'^report-download/$', 'report_download', name='report-download'),
    url(r'^get-entries/$', login_required(ListView.as_view(model=TimesheetEntry, context_object_name='entries_list',
        template_name='tracker/parts/report_part.html')), name='get-entries'),
)
