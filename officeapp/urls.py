from django.urls import path
from . import views

urlpatterns = [
  path('',views.login),
  path('dashboard',views.dashboard,name='dashboard'),
path('login',views.login,name='login'),
path('register',views.register,name='register'),
path('employees/add/', views.add_employee, name='add_employee'),
path('employees/', views.view_employees, name='view_employees'),
path('attendance', views.attendance, name='attendance'),
 path('attendance-view/', views.attendance_view, name='attendance_view'),
path("workreport/add/", views.workreport_add, name="workreport_add"),
path("workreport/view/", views.workreport_view, name="workreport_view"),
path('workreport/delete/<int:report_no>/', views.workreport_delete, name='workreport_delete'),
path('workreport/pdf/<int:report_no>/', views.workreport_pdf, name='workreport_pdf'),

path("expense/add/", views.expense_add, name="expense_add"),
path("expense/view/", views.expense_view, name="expense_view"),
path("expense/delete/<int:report_no>/",views.expense_delete,name="expense_delete"),
path("expense/pdf/<int:report_no>/",views.expense_pdf,name="expense_pdf"),

path('projects', views.projects, name='projects'),
path('reports', views.reports, name='reports'),
path('logout', views.logout_view, name='logout'),




]