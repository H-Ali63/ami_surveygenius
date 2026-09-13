
from django.urls import path
# from search.mismatch_review import MisMatch
# from search.search import Search
# from search.search_v2 import SearchV2
from ama_new.ama_search import Ama_search
from ama_new.views import data_insert,surveyresponse_upload,data_deletion,employee_upload,url_upload

# from search.surveyresponsssss import pope
# from search.views import HomePage,LoginPage,LogoutView

urlpatterns = [
    
    path('', Ama_search.as_view(), name='ama_new'),
    path('data_insert', data_insert, name='data_insert'),
    path('surveyresponse_upload',surveyresponse_upload, name='surveyresponse_upload'),
    path('data_deletion',data_deletion,name='data_deletion'),
    path('employee_upload',employee_upload,name = 'employee_upload'),
    path('url_upload',url_upload,name='url_upload')
   
]