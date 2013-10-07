#coding: utf-8

from django.db import models
from django.db import IntegrityError 
from django.contrib.auth.models import User
from django.db.models.signals import post_save, m2m_changed, post_delete, pre_delete
from django.db.models import F
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _

from guardian.shortcuts import assign_perm

from invite.models import Invitation


class City(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("City")

class Island(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    city = models.ForeignKey(City)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Island")

class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Category")

class Project(models.Model):
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=256, verbose_name=_("Project Name"))
    description = models.TextField(verbose_name=_("Project Description"))
    islands = models.ManyToManyField(Island, verbose_name=_("Island"))  # Usage: project.islands.add(island)
    memberships = models.ManyToManyField(User, through="Membership", 
            related_name="project_belongs", verbose_name=_("Memberships")) 
    category = models.ForeignKey(Category, verbose_name=_("Category"))

    def add_category(self, category):
        project_category, created = ProjectCategory.objects.get_or_create(category=category,
                project=self)

    def add_member(self, user, is_owner=False):
        project_membership, created = Membership.objects.get_or_create(project=self,
                user=user, defaults={'is_owner': is_owner})

    def invite(self, invitee, message):
        Invitation.objects.invite(self.owner, invitee, message, self)

    def member_ids(self):
        return self.memberships.all().values_list('id', flat=True)

    @property
    def get_content_type(self):
        project_type = ContentType.objects.get_for_model(self)
        return project_type

    def get_display_name(self):
        return self.name

    def accept(self, member):
        try:
            self.add_member(member)
        except IntegrityError, e:
            pass


    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Project")

class Membership(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)
    is_owner = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "{} - {}".format(self.user, self.project)

    class Meta:
        unique_together = (("project", "user"), )
        verbose_name = _("Membership")

@receiver(post_save, sender=Project)
def create_owner_membership(sender, instance, created, **kwargs):
    if created:
        instance.add_member(instance.owner, True)

@receiver(pre_delete, sender=Membership)
def delete_invitation(sender, instance, **kwargs):
    to_user = instance.user
    project = instance.project
    from_user = project.owner
    try:
        target_type = ContentType.objects.get_for_model(project)
        Invitation.objects.get(to_user=to_user, from_user=from_user, target_id=project.id, target_type=target_type).delete()
    except Invitation.DoesNotExist, e:
        pass

@receiver(post_save, sender=Membership)
def assign_membership_permission(sender, instance, created, **kwargs):
    if created:
        if instance.is_owner:
            assign_perm('project.add_project', instance.user)


#@receiver(m2m_changed, sender=Flowvisor.slices.through)
#@receiver(m2m_changed, sender=Controller.slices.through)
def on_add_into_slice(sender, instance, action, pk_set, model, **kwargs):
    resource = instance
    if action == 'post_add': #: only handle post_add event
        resource.on_add_into_slice()
