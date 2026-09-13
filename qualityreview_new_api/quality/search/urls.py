
from django.urls import path
from search.mismatch_review import MisMatch
from search.search import Search
from search.search_v2 import SearchV2,assign_projects_view,assign_projects,assigned_delete
from a_app.a_app_quality_views import GeoMismatchView
from a_app.a_app_qualitydashboard import QualityDash
from a_app.a_app_qualityauditviews import QualityAuditView
from search.priority_task import PriorityTasksView

from search.surveyresponsssss import pope,deleted_data
from search.views import HomePage,LoginPage,LogoutView,user_upload

from a_app.exporttext import Export_Response
from a_app.exportdata import ExportData
## images videos import
from a_app.images_videos_download import Images_Export_Data
from a_app.exporttext import Export_new_Response, Download_status
from a_app.exporttext import proxy_download_survey

urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('login', LoginPage.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('geomismatch', GeoMismatchView.as_view(), name='geomismatch'),
    path('qcdash', QualityDash.as_view(), name='qcdash'),
    path('qualityaudit', QualityAuditView.as_view(), name='qcdash'),
    # path('editprofile', EditProfile.as_view(), name='editprofile'),
    path('search',Search.as_view(), name='search'),
    path('mismatch',MisMatch.as_view(), name='mismatch'),
    path('v2',SearchV2.as_view(), name='searchV'),
    path('priority',PriorityTasksView.as_view(),name='priority'),

    path('exportdata', ExportData.as_view(), name='exportdata'),
    path('data', Export_Response.as_view(), name='Export_Response'),
    # path("count",counttt,name='count'),
    # path('pope',pope, name='pope'),
    # path('deleted_data',deleted_data, name='deleted_data'),
    path('user_upload',user_upload, name='user_upload'), #upload users data
    path('assign_projects',assign_projects_view,name='assign_projects'),
    # path('assign-projects/', assign_projects_view, name='assign_projects_view'),
    path('assign-projects/ajax/', assign_projects, name='assign_projects'),
    path('assign-projects/delete/<int:id>', assigned_delete, name='assigned_delete'),

    ### images videos
    path('images/1441', Images_Export_Data.as_view(), name = 'images_videos'),
    path('download_status', Download_status.as_view(), name='download_status'),
    path('download-survey/', proxy_download_survey, name='proxy_download_survey'),

]



# from django.urls import path
# from search.mismatch_review import MisMatch
# from search.search import Search
# from search.search_v2 import SearchV2,assign_projects_view,assign_projects,assigned_delete
# from a_app.a_app_quality_views import GeoMismatchView
# from a_app.a_app_qualitydashboard import QualityDash
# from a_app.a_app_qualityauditviews import QualityAuditView
# from search.priority_task import PriorityTasksView
# # from a_app.a_app_exportdata import ExportData
# from a_app.exporttext import Export_new_Response, Download_status
# # from a_app.images_videos_export import Images_Export_Data
# # from search.surveyorviews import AddSurveyor

# # from search.surveyresponsssss import fetchdata_a_app
# from search.views import HomePage,LoginPage,LogoutView
# urlpatterns = [
#     path('', HomePage.as_view(), name='home'),
#     path('login', LoginPage.as_view(), name='login'),
#     path('logout', LogoutView.as_view(), name='logout'),
#     path('geomismatch', GeoMismatchView.as_view(), name='geomismatch'),
#     path('qcdash', QualityDash.as_view(), name='qcdash'),
#     path('qualityaudit', QualityAuditView.as_view(), name='qcdash'),
#     # path('editprofile', EditProfile.as_view(), name='editprofile'),
#     path('search',Search.as_view(), name='search'),
#     path('mismatch',MisMatch.as_view(), name='mismatch'),
#     path('v2',SearchV2.as_view(), name='searchV'),

#     # path('exportdata', ExportData.as_view(), name='exportdata'),
#     # path('data', Export_new_Response.as_view(), name='Export_Response'),
#     # path("count",counttt,name='count'),
#     # path('pope',fetchdata_a_app, name='fetchdata_a_app'),
#     path('priority',PriorityTasksView.as_view(),name='priority'),

#     # path('dashboard',dashboard,name='dashboard'),
#     # path('user_upload',user_upload,name='user_upload'),
#     path('assign_projects',assign_projects_view,name='assign_projects'),
#     # path('assign-projects/', assign_projects_view, name='assign_projects_view'),
#     path('assign-projects/ajax/', assign_projects, name='assign_projects'),
#     path('assign-projects/delete/<int:id>', assigned_delete, name='assigned_delete'),

#     ##images-videos
#     # path('images/1441',Images_Export_Data.as_view(), name='images_data'),

#     ## add surveyor
#     # path('surveyors/add', AddSurveyor.as_view(), name='addnewsurveyor'),


#     path('download_status', Download_status.as_view(), name='download_status')
    

# ]