from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, pre_delete
from tracker.utils import to_timestamp


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    group = models.CharField(max_length=200)
    cost = models.FloatField(null=True, blank=True)
    color = models.CharField(max_length=15)

    def __unicode__(self):
        return unicode(self.user.get_full_name())


class Category(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False, unique=True)

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        verbose_name_plural = 'Categories'


class Activity(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)
    category = models.ForeignKey(Category, null=False, blank=False)
    rating = models.CharField(max_length=20, null=False, blank=False)

    def __unicode__(self):
        return u'%s - %s' % (self.category, self.name)

    class Meta:
        verbose_name_plural = 'Activities'


class TimesheetEntry(models.Model):
    admin_event = models.BooleanField(default=False)
    trainer = models.CharField(max_length=200, null=True, blank=True)
    trainee = models.CharField(max_length=200, null=True, blank=True)
    trainer_cost = models.FloatField(null=True, blank=True)
    activity = models.ManyToManyField(Activity, related_name='timesheet', null=True, blank=True)
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
        if self.admin_event:
            return u'ADMIN - Comment: %s' % self.comment
        else:
            return u'%s (Trainer) - %s (Trainee) - %s - Comment: %s' % (self.trainer, self.trainee,
                                                                    ' and '.join([i.name for i in self.activity.all()]),
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


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

def delete_user_profile(sender, instance, **kwargs):
    UserProfile.objects.get(user=instance)

post_save.connect(create_user_profile, sender=User)
pre_delete.connect(delete_user_profile, sender=User)