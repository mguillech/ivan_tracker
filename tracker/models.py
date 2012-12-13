from django.db import models
from django.contrib.auth.models import User, Group
from tracker.utils import to_timestamp


class Activity(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        verbose_name_plural = 'Activities'


class TimesheetEntry(models.Model):
    trainer = models.CharField(max_length=200)
    trainee = models.CharField(max_length=200)
    trainer_cost = models.FloatField()
    activity = models.ForeignKey(Activity, related_name='timesheet')
    start = models.DateTimeField()
    end = models.DateTimeField()
    comment = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def start_timestamp(self):
        return to_timestamp(self.start)

    @property
    def end_timestamp(self):
        return to_timestamp(self.end)

    def __unicode__(self):
        return u'%s (Trainer) - %s (Trainee) - %s - Comment: %s' % (self.trainer, self.trainee, self.activity,
                                                                    self.comment or 'No comment')

    @property
    def hourly_cost(self):
        if self.trainer_cost:
            return u'$%.2f' % self.trainer_cost

    @property
    def total_cost(self):
        if self.trainer_cost:
            return u'$%.2f' % float(self.trainer_cost * (self.end - self.start).total_seconds() / 3600)

    class Meta:
        verbose_name_plural = 'Timesheet Entries'


class TrainerCost(models.Model):
    user = models.OneToOneField(User, related_name='trainer_cost')
    cost = models.FloatField()

    def __unicode__(self):
        return u'$%.2f' % self.cost


for group in 'Trainer', 'Trainee':
    _ = Group.objects.get_or_create(name=group)