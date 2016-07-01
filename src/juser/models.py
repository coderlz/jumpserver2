#_*_coding:utf8_*
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser)
import time
# Create your models here.

class UserGroup(models.Model):
    name = models.CharField(max_length=80, unique=True)
    comment = models.CharField(max_length=160,blank=True,null=True)

    def __unicode__(self):
        return self.name

class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError('User mut have an email address')
        user = self.model(email=self.normalize_email(email), name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email=email, name=name, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    username = models.CharField(max_length=80, blank=True, null=True, default='')
    name = models.CharField(max_length=80)
    uuid = models.CharField(max_length=100)
    USER_ROLE_CHOICE = (
        ('SU', 'SuperUser'),
        ('GA', 'GroupAdmin'),
        ('CU', 'CommonUser'),
    )
    role = models.CharField(max_length=2, choices=USER_ROLE_CHOICE, default='CU')
    group = models.ManyToManyField(UserGroup)
    ssh_key_pwd = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField()
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'password', ]

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def __unicode__(self):
        return self.email

    def has_perm(self, perm, object=None):
        return True

    def has_module_perms(self,app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class AdminGroup(models.Model):
    user = models.ForeignKey(User)
    group = models.ForeignKey(UserGroup)

    def __unicode__(self):
        return "%s: %s"(self.user.name, self.group.name)


def upload_to(instance,filename):
        return 'upload/' + str(instance.user.id) + time.strftime("/%Y/%m/%d", time.localtime()) + filename
class Document(models.Model):
    user = models.ForeignKey(User)
    docfile = models.FileField(upload_to=upload_to)