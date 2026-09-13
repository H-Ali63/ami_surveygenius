from django.contrib import admin

from .models import ama_new_data,SurveyResponse_ama,QualityReview_ama

# Register your models here.

@admin.register(ama_new_data)
class ama_dataAdmin(admin.ModelAdmin):
    list_display = ["response_id", "Surveyor_Name", "Respondent_Name"]


@admin.register(SurveyResponse_ama)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ["uid"]


@admin.register(QualityReview_ama)
class QualityReviewAdmin(admin.ModelAdmin):
    list_display = ["uid", "project_name", "surveyor_name"]