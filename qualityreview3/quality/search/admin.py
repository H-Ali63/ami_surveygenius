from __future__ import unicode_literals

from django.contrib import admin
from search.models import *
from django import forms

# Register your models here.
class DesignationChoiceField(forms.ModelChoiceField):
     def label_from_instance(self, obj):
         return "%s, %s" % (obj.name, obj.department.name)

class DepartmentChoiceField(forms.ModelChoiceField):
     def label_from_instance(self, obj):
         return "%s" % (obj.name)

class LocationChoiceField(forms.ModelChoiceField):
     def label_from_instance(self, obj):
         return "%s" % (obj.name)

class OfficeLocationChoiceField(forms.ModelChoiceField):
     def label_from_instance(self, obj):
         return "%s" % (obj.name)

class LayerChoiceField(forms.ModelChoiceField):
     def label_from_instance(self, obj):
         return "%s" % (obj.name)

class StateChoiceField(forms.ModelChoiceField):
     def label_from_instance(self, obj):
         return "%s" % (obj.name)

class LanguageChoiceField(forms.ModelChoiceField):
     def label_from_instance(self, obj):
         return "%s, %s" % (obj.name, obj.longform)

class ProjectChoiceField(forms.ModelChoiceField):
     def label_from_instance(self, obj):
         return "%s, %s" % (obj.name, obj.state.name)

class UserChoiceField(forms.ModelChoiceField):
     def label_from_instance(self, obj):
         return "%s %s" % (obj.user.first_name, obj.user.last_name)


# Admin registry
class DepartmentAdminForm(forms.ModelForm):
    hod = UserChoiceField(queryset=Employee.objects.all())
    class Meta:
        model = Department
        fields = '__all__'

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_hod',)
    form = DepartmentAdminForm

    def get_hod(self, obj):
        try:
            return obj.hod.user.first_name+' '+obj.hod.user.last_name
        except Exception as e:
            return '-'

admin.site.register(Department, DepartmentAdmin)

class LayerAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Layer, LayerAdmin)

# Designation admin
class DesignationAdminForm(forms.ModelForm):
    department = DepartmentChoiceField(queryset=Department.objects.all())
    layer = LayerChoiceField(queryset=Layer.objects.all())
    class Meta:
        model = Department
        fields = '__all__'

class DesignationAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_department',)
    form = DesignationAdminForm

    def get_department(self, obj):
        return obj.department.name

admin.site.register(Designation, DesignationAdmin)
# End of Designation admin

class StateAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(State, StateAdmin)


class OfficeLocationAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(OfficeLocation, OfficeLocationAdmin)

class LocationAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Location, LocationAdmin)

# Employee Admin
class EmployeeAdminForm(forms.ModelForm):
    designation = DesignationChoiceField(queryset=Designation.objects.all())
    location = LocationChoiceField(queryset=Location.objects.all())
    office_location = OfficeLocationChoiceField(queryset=OfficeLocation.objects.all())

    class Meta:
        model = Employee
        fields = '__all__'

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_name')
    search_fields = ['user_id__first_name', 'user_id__last_name', 'employee_id']
    form = EmployeeAdminForm

    def get_name(self, obj):
        try:
            return obj.user.first_name+' '+obj.user.last_name
        except Exception as e:
            return '-'

admin.site.register(Employee, EmployeeAdmin)
# End of Employee Admin



# End of Hotels Admin


class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'longform')

admin.site.register(Language, LanguageAdmin)

class VerificationStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(VerificationStatus, VerificationStatusAdmin)

class ProjectAdminForm(forms.ModelForm):
    state = StateChoiceField(queryset=State.objects.all())
    language = LanguageChoiceField(queryset=Language.objects.all())
    class Meta:
        model = Project
        fields = '__all__'

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    form = ProjectAdminForm

admin.site.register(Project, ProjectAdmin)





class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('uid', 'verification_date', 'get_projectname', 'get_verification_status')
    search_fields = ('uid',)
    list_filter = ('verification_status__name',)

    def get_projectname(self, obj):
        return obj.project.name

    def get_verification_status(self, obj):
        return obj.verification_status.name

admin.site.register(SurveyResponse, SurveyResponseAdmin)


admin.site.register(QualityReview)
admin.site.register(QualityReviewMismatch)

admin.site.register(duplicateSurveyResponse)