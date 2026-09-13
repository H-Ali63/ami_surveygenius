# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone



from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings

# Create your models here.

GENDER_CHOICES = (
                    ('NA', 'NA'),
                    ('M', 'Male'),
                    ('F', 'Female')
                  )

MARITAL_CHOICES = (
                    ('NA', 'NA'),
                    ('Single', 'Single'),
                    ('Married', 'Married'),
                    ('Divorced', 'Divorced'),
                    ('Widowed', 'Widowed')
                  )


class Department(models.Model):
    name = models.CharField(max_length=100, blank=True, null=False, unique=True)
    # hod = models.IntegerField(max_length=11,null=True)
    hod = models.ForeignKey('Employee', null=True, blank=True, on_delete=models.SET_NULL, related_name='hod_department')


class Layer(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False, unique=True)

class Designation(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False, unique=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='department_designation')
    layer = models.ForeignKey(Layer, on_delete=models.CASCADE)

class State(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True, unique=False)

class Location(models.Model):
    
    name = models.CharField(max_length=100, blank=False, null=False, unique=False)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

class OfficeLocation(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False, unique=True)
    location = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL)
    address = models.CharField(max_length=100, blank=True, null=True, unique=False)

class Employee(models.Model):
    # user = models.CharField(max_length=100, blank=True, null=True, unique=False)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE, related_name='user_employee')
    # profile_pic = models.ImageField(upload_to='media/profile_pics', blank=True, null=True)
    # old_code = models.CharField(max_length=100, blank=True, null=True)
    designation = models.ForeignKey(Designation, null=True, on_delete=models.SET_NULL, related_name='designation_employee')
    gender = models.CharField(max_length=100, blank=False, null=False, choices=GENDER_CHOICES, default='NA')
    # marital_status = models.CharField(max_length=100, blank=False, null=False, choices=MARITAL_CHOICES, default='NA')
    employee_id = models.CharField(max_length=100, blank=False, null=False, unique=True)
    # joining_date = models.DateField(auto_now=False, null=True, blank=True)
    # leaving_date = models.DateField(auto_now=False, null=True, blank=True)
    # joining_date = models.CharField(max_length=10, null=True, blank=True)
    # leaving_date = models.CharField(max_length=10, null=True, blank=True)
    # date_of_birth = models.DateField(auto_now=False, null=True, blank=True)
    date_of_birth = models.CharField(max_length=10, null=True, blank=True)
    # phone_number = models.CharField(max_length=100, null=True, blank=True)
    location = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL)
    office_location = models.ForeignKey(OfficeLocation, null=True, blank=True, on_delete=models.SET_NULL)
    address = models.CharField(max_length=700, blank=True, null=True, unique=False)
    # active = models.BooleanField(default=False, blank=True)
    # pms_allowed_interval = models.IntegerField(default=0, blank=True)
    # adhar_card = models.CharField(max_length=12, blank=True, null=True, unique=True)
    # adhar_pic = models.ImageField(upload_to='media/', blank=True, null=True)
    user_role = models.CharField(max_length=100, default="user",null=True, blank=True)
    # project = models.CharField(max_length=100, null=True, blank=True)


    def get_profile_pic(self):
        return self.profile_pic

    def save(self, *args, **kwargs):
        if self.user != None:
            if Employee.objects.filter(employee_id=self.employee_id).count() > 0:
                if Employee.objects.get(employee_id=self.employee_id).user == self.user:
                    # Save the same id without any change
                    pass
                else:
                    try:
                        pass
                    except Exception as e:
                        # Change the existing id and handle duplicates
                        self.employee_id = int(Employee.objects.all().order_by('-employee_id')[0].employee_id) + 1
            else:
                # Save the same id without any change
                pass
        else:
            if User.objects.filter(username=self.employee_id).count() > 0:
                pass
            else:
                self.employee_id = int(Employee.objects.all().order_by('-employee_id')[0].employee_id) + 1


        super(Employee, self).save(*args, **kwargs)



class A_app_surveyors(models.Model):
    a_app_id = models.IntegerField(unique=True, verbose_name='a_app_surveyor_id')
    surveyor_name = models.CharField(max_length=100, blank=False, null=False, unique=True)
    mobile_number = models.CharField(max_length = 10, blank=False, null=False, unique=True)
    emp_id = models.OneToOneField(Employee, null=True, blank=True, on_delete=models.SET_NULL, related_name='surveyor_user')

    def __str__(self):
        return self.a_app_id + " " +self.emp_id




class Language(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False, unique=True)
    longform = models.CharField(max_length=100, blank=False, null=False, unique=False)


class Project(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False, unique=True)
    capi_checklist_id = models.IntegerField(null=True, blank=True)
    state = models.ForeignKey(State, null=True, on_delete=models.SET_NULL)

    # startdate = models.CharField(max_length=10,null=True, blank=True)
    startdate = models.DateField(auto_now=False, null=True, blank=True)
    enddate = models.DateField(auto_now=False, null=True, blank=True)
    geocodes_available = models.BooleanField(default=False)
    nccs = models.BooleanField(default=False)
    language = models.ForeignKey(Language, null=True, on_delete=models.SET_NULL)
    remarks = models.CharField(max_length=100, blank=True, null=True)
    active = models.BooleanField(default=True)
    verification_percent = models.IntegerField(blank=True, default=10)
    verification_percent_backcheck = models.IntegerField(blank=True, default=20)
    frpmdashboard_flag = models.BooleanField(default=False)
    pull_data = models.BooleanField(default=False)
    is_gas_activity = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk)+ '. '+ str(self.name)
    
class VerificationStatus(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False, unique=True)
    

class SurveyResponse(models.Model):
    uid = models.CharField(max_length=100, blank=False, null=False,  db_index=True, unique=True)
    uidi = models.IntegerField(null=True, blank=True, db_index=True)
    user = models.ForeignKey(Employee, blank=True, null=True, on_delete=models.SET_NULL, related_name='response_assigned_to_user')
    project = models.ForeignKey(Project, blank=True, null=True, on_delete=models.SET_NULL, related_name='response_to_project')
    surveyor = models.ForeignKey(Employee, blank=True, null=True, on_delete=models.SET_NULL, related_name='response_from_surveyor')
    verification_status = models.ForeignKey(VerificationStatus, blank=True, null=True, on_delete=models.SET_NULL, related_name='response_verification_status')
    otp_verified = models.BooleanField(default=False, blank=True)
    params = models.TextField(default="{}", blank=True)
    remarks = models.TextField(default="{}", blank=True)
    verification_date = models.DateTimeField(auto_now=True)
    send_to_surveyor = models.BooleanField(default=False, blank=True)
    allocated_survey = models.CharField(max_length=10, blank=True, null=True)
    response_date = models.DateField(
        null=True,
        blank=True,
        db_index=True
    )

    # NEW: denormalized Field Researcher value.
    # This removes the need to search inside params JSON/TextField.
    teamleader = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        db_index=True,
    )

    class Meta:
        indexes = [
            models.Index(
                fields=['-verification_date'],
                name='sr_verification_date_idx',
            ),

            models.Index(
                fields=['project', '-verification_date'],
                name='sr_project_date_idx',
            ),

            models.Index(
                fields=['surveyor', '-verification_date'],
                name='sr_surveyor_date_idx',
            ),

            models.Index(
                fields=['user', '-verification_date'],
                name='sr_user_date_idx',
            ),

            models.Index(
                fields=['verification_status', '-verification_date'],
                name='sr_status_date_idx',
            ),

            models.Index(
                fields=['project', 'surveyor', '-verification_date'],
                name='sr_project_surveyor_date_idx',
            ),

            # NEW OPTIMIZATION INDEX
            models.Index(
                fields=['teamleader', '-verification_date'],
                name='sr_fr_date_idx',
            ),
        ]

    

    def __str__(self):
        return self.uid

class duplicateSurveyResponse(models.Model):
    uid = models.CharField(max_length=100, blank=False, null=False, db_index=True)
    uidi = models.IntegerField(null=True, blank=True, db_index=True)
    user = models.ForeignKey(Employee, blank=True, null=True, on_delete=models.SET_NULL, related_name='responsrs')
    project = models.ForeignKey(Project, blank=True, null=True, on_delete=models.SET_NULL, related_name='responsef')
    surveyor = models.ForeignKey(Employee, blank=True, null=True, on_delete=models.SET_NULL, related_name='responseg')
    verification_status = models.ForeignKey(VerificationStatus, blank=True, null=True, on_delete=models.SET_NULL, related_name='responsee')
    otp_verified = models.BooleanField(default=False, blank=True)
    params = models.TextField(default="{}", blank=True)
    remarks = models.TextField(default="{}", blank=True)
    verification_date = models.DateTimeField(auto_now=True)
    send_to_surveyor = models.BooleanField(default=False, blank=True)
    allocated_survey = models.CharField(max_length=10, blank=True, null=True)


class IssueList(models.Model):
    issue_id = models.CharField(max_length=10,null=False,blank=False,unique=True)
    section = models.CharField(max_length=20,null=False,blank=False)
    issues = models.TextField(max_length=500,null=False,blank=False)
    related_question = models.TextField(max_length=700,null=False,blank=False)






# migrating quality table from quality Database to surveygenius
class QualityReview(models.Model):
    id=models.AutoField(primary_key=True);
    uid=models.IntegerField(blank=False,null=False)
    project_name = models.CharField(max_length=120,blank=True,null=True);
    surveyor_name = models.CharField(max_length=60,blank=True,null=True);
    fr_name = models.CharField(max_length=60,blank=True,null=True);
    # interview_date = models.DateField(blank=True,null=True);
    interview_date = models.CharField(max_length=15, blank=True, null=True);
    interview_duration = models.CharField(max_length=60,blank=True,null=True);
    quality_auditor = models.CharField(max_length=60,blank=True,null=False);
    auditor_date = models.DateField(blank=False,null=True);
    # auditor_date = models.CharField(max_length=10, blank=True, null=True);
    skipping = models.CharField(max_length=60,blank=True,null=True);
    knowledge = models.CharField(max_length=60, blank=True, null=True);
    recordings = models.CharField(max_length=60, blank=True, null=True);
    voice = models.CharField(max_length=60, blank=True, null=True);
    remarksSection_A = models.TextField(max_length=2000,blank=False,null=False);
    skills = models.CharField(max_length=50,blank=True,null=True);
    answer = models.CharField(max_length=50, blank=True, null=True);
    convince = models.CharField(max_length=50, blank=True, null=True);
    remarksSection_B = models.TextField(max_length=2000,blank=False,null=False);
    polite = models.CharField(max_length=50, blank=True, null=True);
    speech = models.CharField(max_length=50, blank=True, null=True);
    professional = models.CharField(max_length=50, blank=True, null=True);
    remarksSection_C = models.TextField(max_length=2000,blank=False,null=False);
    variation = models.CharField(max_length=50, blank=True, null=True);
    survey = models.CharField(max_length=50, blank=True, null=True);
    # New Additional
    variation_reason = models.ForeignKey(IssueList, blank=True, null=True, on_delete=models.SET_NULL,related_name='issue_list_variation_reason')
    remarksSection_E_variation_1 = models.TextField(max_length=700, blank=True, null=True);
    force_survey_reason = models.ForeignKey(IssueList, blank=True, null=True, on_delete=models.SET_NULL,related_name='issue_list_force_survey_reason')
    remarksSection_E_force_survey_1 = models.TextField(max_length=700, blank=True, null=True);

    movement = models.CharField(max_length=50, blank=True, null=True);
    tagging = models.CharField(max_length=50, blank=True, null=True);
    fake = models.TextField(max_length=700, blank=True, null=True);
    remarksSection_D = models.TextField(max_length=700,blank=False,null=False);
    totalscore = models.IntegerField(blank=False, null=False);
    # created_at = models.DateTimeField(blank=False, null=False);
    created_at = models.DateTimeField(auto_now=True);
    quality_auditor_id = models.IntegerField(blank=False,null=False,default=404);
    is_fake_form = models.BooleanField(blank=False,null=False,default=False);
    version = models.TextField(max_length=100,blank=False,null=False,default='Nov_2019-June_2020')

    # Section A new format
    question_skipping_incomplete_recordings = models.CharField(max_length=60,blank=True,null=True);
    remarksSection_A_skipping_incomplete_recordings_1 = models.TextField(max_length=700, blank=True, null=True);
    remarksSection_A_skipping_incomplete_recordings_2 = models.TextField(max_length=700, blank=True, null=True);
    # question_skipping_incomplete_recordings_reason = models.CharField(max_length=700, blank=True, null=True);
    question_skipping_incomplete_recordings_reason = models.ForeignKey(IssueList, blank=True, null=True, on_delete=models.SET_NULL,related_name='issue_list')

    # Section B new format
    question_subject_knowledge = models.CharField(max_length=60, blank=True, null=True);
    remarksSection_B_question_subject_knowledge_1 = models.TextField(max_length=700, blank=True, null=True);
    remarksSection_B_question_subject_knowledge_2 = models.TextField(max_length=700, blank=True, null=True);
    question_subject_knowledge_reason = models.ForeignKey(IssueList, blank=True, null=True, on_delete=models.SET_NULL,related_name='issue_list_question_subject_knowledge_reason')

    # Section C new format
    voice_clarity = models.CharField(max_length=60, blank=True, null=True);
    remarksSection_C_voice_clarity_1 = models.TextField(max_length=700, blank=True, null=True);
    remarksSection_C_voice_clarity_2 = models.TextField(max_length=700, blank=True, null=True);
    voice_clarity_reason = models.ForeignKey(IssueList, blank=True, null=True, on_delete=models.SET_NULL,related_name='issue_list_voice_clarity_reason')

    questioning_technique = models.CharField(max_length=60, blank=True, null=True);
    remarksSection_C_questioning_technique_1 = models.TextField(max_length=700, blank=True, null=True);
    remarksSection_C_questioning_technique_2 = models.TextField(max_length=700, blank=True, null=True);
    questioning_technique_reason = models.ForeignKey(IssueList, blank=True, null=True, on_delete=models.SET_NULL,related_name='issue_list_questioning_technique_reason')

    convencing_skills = models.CharField(max_length=60, blank=True, null=True);
    remarksSection_C_convencing_skills_1 = models.TextField(max_length=700, blank=True, null=True);
    remarksSection_C_convencing_skills_2 = models.TextField(max_length=700, blank=True, null=True);
    convencing_skills_reason = models.ForeignKey(IssueList, blank=True, null=True, on_delete=models.SET_NULL,related_name='issue_list_convencing_skills_reason')


    # Section D new format
    polite_courteous = models.CharField(max_length=60, blank=True, null=True);
    remarksSection_D_polite_courteous_1 = models.TextField(max_length=700, blank=True, null=True);
    remarksSection_D_polite_courteous_2 = models.TextField(max_length=700, blank=True, null=True);
    polite_courteous_reason = models.ForeignKey(IssueList, blank=True, null=True, on_delete=models.SET_NULL,related_name='issue_list_polite_courteous_reason')

    rate_of_speech = models.CharField(max_length=60, blank=True, null=True);
    remarksSection_D_rate_of_speech_1 = models.TextField(max_length=700, blank=True, null=True);
    remarksSection_D_rate_of_speech_2 = models.TextField(max_length=700, blank=True, null=True);
    rate_of_speech_reason = models.ForeignKey(IssueList, blank=True, null=True, on_delete=models.SET_NULL,related_name='issue_list_rate_of_speech_reason')

    professionalism_energetic_enthusiastic = models.CharField(max_length=60, blank=True, null=True);
    remarksSection_D_professionalism_energetic_enthusiastic_1 = models.TextField(max_length=700, blank=True, null=True);
    remarksSection_D_professionalism_energetic_enthusiastic_2 = models.TextField(max_length=700, blank=True, null=True);
    professionalism_energetic_enthusiastic_reason =models.ForeignKey(IssueList, blank=True, null=True, on_delete=models.SET_NULL,related_name='issue_list_professionalism_energetic_enthusiastic_reason')

    def __str__(self):
        return str(self.uid)
    
class PriorityTasksSchedulesID(models.Model):   ## addedd
    task_id = models.IntegerField(blank=False,null=False,primary_key=True);
    task_created_by = models.CharField(max_length=128,blank=False,null=False);
    task_created_on = models.DateTimeField(auto_now=False, blank=True, null=True);


class AccessToken(models.Model):
    token = models.CharField(max_length=1000,blank=False,null=False)
    created_at = models.DateTimeField(auto_now_add=True)
 
    @classmethod
    def get_existing_token(cls):
        """
        Fetch the token if it exists.
        """
        return cls.objects.first()
 
    @classmethod
    def save_new_token(cls, new_token):
        """
        Save a new token, replacing the old one if necessary.
        """
        cls.objects.all().delete()  # Ensure only one token exists
        cls.objects.create(token=new_token)


class QualityReviewMismatch(models.Model):
    id = models.AutoField(primary_key=True);
    uid = models.IntegerField(blank=False, null=False)
    project_name = models.CharField(max_length=120, blank=True, null=True);
    surveyor_name = models.CharField(max_length=60, blank=True, null=True);
    fr_name = models.CharField(max_length=60, blank=True, null=True);
    # interview_date = models.DateField(blank=True, null=True);
    interview_date = models.CharField(max_length=10, blank=True, null=True);
    interview_duration = models.CharField(max_length=60, blank=True, null=True);
    quality_auditor = models.CharField(max_length=60, blank=True, null=False);
    auditor_date = models.DateField(blank=False, null=True);
    # auditor_date = models.CharField(max_length=10, blank=True, null=True);
    review = models.TextField(max_length=500, blank=False, null=False);



class a_app_data(models.Model):
    id = models.AutoField(primary_key=True);
    choice_id = models.IntegerField(blank=True, null=True)
    id1 = models.IntegerField(blank=True, null=True)
    surveyor_name = models.CharField(max_length=60, blank=True, null=True);
    surveyor_id = models.IntegerField(blank=True, null=True)
    Respondent_Name = models.CharField(max_length=60, blank=True, null=True);
    question_name = models.CharField(max_length=500, blank=True, null=True);
    question_title = models.CharField(max_length=2000, blank=True, null=True);
    Response = models.CharField(max_length=4000, blank=True, null=True);
    mobile_no = models.CharField(max_length=60, blank=True, null=True);
    survey_name = models.CharField(max_length=400, blank=True, null=True);
    area = models.CharField(max_length=60, blank=True, null=True);
    lat = models.CharField(max_length=60, blank=True, null=True);
    lon = models.CharField(max_length=60, blank=True, null=True);
    audio_recording = models.CharField(max_length=40, blank=True, null=True);
    end_time = models.CharField(max_length=40, blank=True, null=True);
    # created_at = models.DateTimeField(auto_now_add=True, blank=True);
    # created_at = models.DateTimeField(default=timezone.now);
    # updated_at = models.DateTimeField(auto_now=True);
    starttime = models.CharField(max_length=60, blank=True, null=True);


class Assignment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('employee', 'project')  # Prevent duplicate assignments



class AllDataDump(models.Model):
    project = models.ForeignKey(Project, blank=True, null=True, on_delete=models.SET_NULL, related_name='a_app_alldata_to_project')
    checkpoints = models.TextField(blank=True, null=True)
    checkpoints_raw = models.TextField(blank=True, null=True)
    uidi = models.IntegerField(null=True, blank=True, db_index=True)
    uid = models.CharField(blank=True, null=True, max_length=10, db_index=True)
    rawdata = models.TextField(blank=True, null=True)
    rawdata_raw = models.TextField(blank=True, null=True)
    image_data = models.TextField(blank=True, null=True)


