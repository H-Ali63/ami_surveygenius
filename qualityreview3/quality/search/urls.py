
from django.urls import path
from search.mismatch_review import MisMatch
from search.search import Search
from search.search_v2 import SearchV2,assign_projects_view,assign_projects,assigned_delete

from search.surveyresponsssss import pope,deleted_data
from search.views import HomePage,LoginPage,LogoutView,user_data

urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('login', LoginPage.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    # path('editprofile', EditProfile.as_view(), name='editprofile'),
    path('search',Search.as_view(), name='search'),
    path('mismatch',MisMatch.as_view(), name='mismatch'),
    path('v2',SearchV2.as_view(), name='searchV'),
    # path("count",counttt,name='count'),
    path('pope',pope, name='pope'),
    path('deleted_data',deleted_data, name='deleted_data'),
    path('user_data',user_data, name='user_data'), #upload users data
    path('assign_projects',assign_projects_view,name='assign_projects'),
    # path('assign-projects/', assign_projects_view, name='assign_projects_view'),
    path('assign-projects/ajax/', assign_projects, name='assign_projects'),
    path('assign-projects/delete/<int:id>', assigned_delete, name='assigned_delete')

]