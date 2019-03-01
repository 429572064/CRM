"""CRM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from employee import views
from rbac import urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/',views.index),

    path('login/',views.login),
    path('reg/',views.reg),
    path('get_auth_code/',views.get_auth_code),

    path('customer_view/',views.CustomerView.as_view(),name="customer_view"),
    path('customer/add/',views.AddEditCustomerView.as_view(),name="add_customer"),
    re_path('^customer/edit/(\d+)/$',views.AddEditCustomerView.as_view(),name="edit_customer"),
    path('mycustomers/',views.CustomerView.as_view(),name="mycustomers"),

    path('consult_record/',views.ConsultRecordView.as_view(),name="consult_record"),
    re_path('^consult_record/edit/(\d+)/$',views.AddEditConsultRecordView.as_view(),name="edit_consult_record"),
    path('consult_record/add/',views.AddEditConsultRecordView.as_view(),name="add_consult_record"),

    path('class_study_record/',views.ClassStudyRecordView.as_view(),name='class_study_record'),
    path('class_study_record/add/',views.AddEditClassStudyRecordView.as_view(),name='add_class_study_record' ),
    re_path('^class_study_record/edit/(\d+)/$',views.AddEditClassStudyRecordView.as_view(),name='edit_class_study_record' ),
    re_path('^class_study_record/delete/(\d+)/$',views.DeleteClassStudyRecordView.as_view(),name='delete_class_study_record' ),

    path('student_study_record/', views.StudentStudyRecordView.as_view(), name='student_study_record'),
    path('student_study_record/add/', views.AddStudentStudyRecordView.as_view(), name='add_student_study_record'),
    re_path('^student_study_record/delete/(\d+)/$',views.DeleteStudentStudyRecordView.as_view(),name='delete_student_study_record' ),

    re_path('^class_score_view/(\d+)/$', views.ClassScoreView.as_view(), name='class_score'),
    path('class_score_view/', views.ClassScoreView.as_view()),
    path('show_deal_view/',views.ShowDealView.as_view()),

    path('permission/', include('rbac.urls')),
    path('rbac/', include('rbac.urls')),

]
