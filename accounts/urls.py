from django.urls import path
from .forms import EmailAuthenticationForm
from . import views


urlpatterns = [
    #basic pages
    path('', views.index, name='home'),
    
    #authentication urls
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),    

    #app functionality
    path('departments/', views.department_view, name='department_list'),
    path('materials/<slug:slug>/', views.material_list_view, name='material_list'),

    #protected upload route    
    path('materials-upload/', views.material_upload_view, name='materials_upload'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    #download tracking
    path('download/<int:pk>/', views.track_download, name='track_download'),

    path('feedback/', views.feedback_view, name='feedback'),

    # AJAX endpoints
    path('ajax/load-departments/', views.load_departments, name='ajax_load_departments'),
  
    path('load-semesters/', views.load_semesters, name='load_semesters'),
]
