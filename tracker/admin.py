from django.contrib import admin
from tracker.models import Activity, TimesheetEntry, TrainerCost

admin.site.register(Activity)
admin.site.register(TimesheetEntry)
admin.site.register(TrainerCost)
