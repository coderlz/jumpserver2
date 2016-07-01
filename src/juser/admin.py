from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import (
    User,
    UserGroup,
    AdminGroup,
    Document)
from django import forms
# Register your models here.


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(label='password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='confirm password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'password2']

    def clean_password2(self):
        password = self.cleaned_data.get['password']
        password2 = self.cleaned_data.get['password2']
        if password != password2:
            raise forms.ValidationError('Password must match')
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data.get['password'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'is_active', 'is_admin', 'role']

    def clean_password(self):
        return self.initial['password']


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ['email', 'name', 'role']
    list_filter = ['is_admin', ]
    fieldsets = (
        (None, {'fields': ('email', 'uuid', 'name', 'group', 'role')}),
        ('Personal info', {'fields': ('last_login',)}),
        ('Permission', {'fields': ('is_admin',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'uuid', 'name', 'group', 'role', 'password', 'password2')
        })
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)
admin.site.register(UserGroup)
admin.site.register(AdminGroup)
admin.site.register(Document)
admin.site.unregister(Group)