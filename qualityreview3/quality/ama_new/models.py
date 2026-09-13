from django.db import models

# Create your models here.
from search.models import *

class ama_new_data(models.Model):
    id = models.AutoField(primary_key=True)
    response_id = models.CharField(max_length=40,unique=True)
    Surveyor_Name = models.CharField(max_length=40)
    Survey_name = models.CharField(max_length=100)
    Respondent_Name = models.CharField(max_length=100)
    Respondent_location = models.CharField(max_length=500)
    State = models.CharField(max_length=50,default=None)
    City = models.CharField(max_length=50,default=None)
    Start_time = models.CharField(max_length=50,default=None) 
    Completion_time = models.CharField(max_length=50,default=None)
    Time_taken = models.CharField(max_length=50,default=None)
    Lat = models.CharField(max_length=50)
    Long = models.CharField(max_length=50)
    Ama_audio_Url = models.URLField(max_length = 1000,null=True)                         
    Ama_response_Url = models.URLField(max_length = 500,null=True)


class SurveyResponse_ama(models.Model):
    uid = models.CharField(max_length=100, blank=False, null=False, db_index=True)
    # uidi = models.IntegerField(null=True, blank=True, db_index=True)
    user = models.ForeignKey(Employee, blank=True, null=True, on_delete=models.SET_NULL, related_name='ama_new_response_assigned_to_user')
    project = models.ForeignKey(Project, blank=True, null=True, on_delete=models.SET_NULL, related_name='ama_new_response_to_project')
    # project = models.CharField(max_length=100)
    surveyor = models.ForeignKey(Employee, blank=True, null=True, on_delete=models.SET_NULL, related_name='ama_new_response_from_surveyor')
    verification_status = models.ForeignKey(VerificationStatus, blank=True, null=True, on_delete=models.SET_NULL, related_name='ama_new_response_verification_status')
    otp_verified = models.BooleanField(default=False, blank=True)
    params = models.TextField(default="{}", blank=True)
    remarks = models.TextField(default="{}", blank=True)
    uploaded_date = models.DateTimeField(auto_now=True)
    send_to_surveyor = models.BooleanField(default=False, blank=True)
    allocated_survey = models.CharField(max_length=10, blank=True, null=True)

class QualityReview_ama(models.Model):
    id=models.AutoField(primary_key=True);
    uid = models.CharField(max_length=100, blank=False, null=False)
    project_name = models.CharField(max_length=120,blank=True,null=True);
    surveyor_name = models.CharField(max_length=60,blank=True,null=True);
    # fr_name = models.CharField(max_length=60,blank=True,null=True);
    interview_date = models.DateField(blank=True,null=True);
    # interview_date = models.CharField(max_length=10, blank=True, null=True);
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
    variation_reason = models.ForeignKey(IssueList, blank=True, null=True, on_delete=models.SET_NULL,related_name='ama_new_issue_list_variation_reason')
    remarksSection_E_variation_1 = models.TextField(max_length=700, blank=True, null=True);
    force_survey_reason = models.ForeignKey(IssueList, blank=True, null=True, on_delete=models.SET_NULL,related_name='ama_new_issue_list_force_survey_reason')
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
    #   version = models.TextField(max_length=100,blank=False,null=False,default='Nov_2019-June_2020')

    # Section A new format
    question_skipping_incomplete_recordings = models.CharField(max_length=60,blank=True,null=True);
    remarksSection_A_skipping_incomplete_recordings_1 = models.TextField(max_length=700, blank=True, null=True);
    remarksSection_A_skipping_incomplete_recordings_2 = models.TextField(max_length=700, blank=True, null=True);
    # question_skipping_incomplete_recordings_reason = models.CharField(max_length=700, blank=True, null=True);
    question_skipping_incomplete_recordings_reason = models.ForeignKey(IssueList, blank=True, null=True, on_delete=models.SET_NULL,related_name='ama_new_issue_list')

    # Section B new format
    question_subject_knowledge = models.CharField(max_length=60, blank=True, null=True);
    remarksSection_B_question_subject_knowledge_1 = models.TextField(max_length=700, blank=True, null=True);
    remarksSection_B_question_subject_knowledge_2 = models.TextField(max_length=700, blank=True, null=True);
    question_subject_knowledge_reason = models.ForeignKey(IssueList, blank=True, null=True, on_delete=models.SET_NULL,related_name='ama_new_issue_list_question_subject_knowledge_reason')

    # Section C new format
    voice_clarity = models.CharField(max_length=60, blank=True, null=True);
    remarksSection_C_voice_clarity_1 = models.TextField(max_length=700, blank=True, null=True);
    remarksSection_C_voice_clarity_2 = models.TextField(max_length=700, blank=True, null=True);
    voice_clarity_reason = models.ForeignKey(IssueList, blank=True, null=True, on_delete=models.SET_NULL,related_name='ama_new_issue_list_voice_clarity_reason')

    questioning_technique = models.CharField(max_length=60, blank=True, null=True);
    remarksSection_C_questioning_technique_1 = models.TextField(max_length=700, blank=True, null=True);
    remarksSection_C_questioning_technique_2 = models.TextField(max_length=700, blank=True, null=True);
    questioning_technique_reason = models.ForeignKey(IssueList, blank=True, null=True, on_delete=models.SET_NULL,related_name='ama_new_issue_list_questioning_technique_reason')

    convencing_skills = models.CharField(max_length=60, blank=True, null=True);
    remarksSection_C_convencing_skills_1 = models.TextField(max_length=700, blank=True, null=True);
    remarksSection_C_convencing_skills_2 = models.TextField(max_length=700, blank=True, null=True);
    convencing_skills_reason = models.ForeignKey(IssueList, blank=True, null=True, on_delete=models.SET_NULL,related_name='ama_new_issue_list_convencing_skills_reason')


    # Section D new format
    polite_courteous = models.CharField(max_length=60, blank=True, null=True);
    remarksSection_D_polite_courteous_1 = models.TextField(max_length=700, blank=True, null=True);
    remarksSection_D_polite_courteous_2 = models.TextField(max_length=700, blank=True, null=True);
    polite_courteous_reason = models.ForeignKey(IssueList, blank=True, null=True, on_delete=models.SET_NULL,related_name='ama_new_issue_list_polite_courteous_reason')

    rate_of_speech = models.CharField(max_length=60, blank=True, null=True);
    remarksSection_D_rate_of_speech_1 = models.TextField(max_length=700, blank=True, null=True);
    remarksSection_D_rate_of_speech_2 = models.TextField(max_length=700, blank=True, null=True);
    rate_of_speech_reason = models.ForeignKey(IssueList, blank=True, null=True, on_delete=models.SET_NULL,related_name='ama_new_issue_list_rate_of_speech_reason')

    professionalism_energetic_enthusiastic = models.CharField(max_length=60, blank=True, null=True);
    remarksSection_D_professionalism_energetic_enthusiastic_1 = models.TextField(max_length=700, blank=True, null=True);
    remarksSection_D_professionalism_energetic_enthusiastic_2 = models.TextField(max_length=700, blank=True, null=True);
    professionalism_energetic_enthusiastic_reason =models.ForeignKey(IssueList, blank=True, null=True, on_delete=models.SET_NULL,related_name='ama_new_issue_list_professionalism_energetic_enthusiastic_reason')

