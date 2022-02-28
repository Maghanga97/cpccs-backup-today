from django.contrib import admin
from django.urls import path
from django.views.static import serve
from django.conf.urls import url
from django.conf import settings
from incidents.views import  incident_pdf, overall_report, department_incidents_types, incidents_view, incidents_types, incidents_list, department_incidents, registration_view, add_department, manage_users, admin_view, details, edit_user_view, main_admin_panel, login
from incidents.db_insert import change_user, insert_function, registration_back_end, add_department_back_end, assign_user_incident, change_user

urlpatterns = [
    path('', incidents_view),
    path('insert_data/', insert_function),
    path('register/<reg_session_key>/', registration_view),
    path('add/<dept_session_key>/', add_department),
    path('register_backend/', registration_back_end),
    path('admin-dashboard/<str:user>/<str:session>/', admin_view),
    path('add_backend/', add_department_back_end),
    path('more-details/<user>/<incident>/<clicked_from>/', details, name='incident_details'),
    path('assign/', assign_user_incident),
    path('pdf/<reference>/', incident_pdf),
    path('report/', overall_report),
    path('view_user/<clicked_from>/<admin>/<user_id>/', edit_user_view),
    path('edit/', change_user),
    path('login/', login),
    path('main-dashboard/<user>/<session>/', main_admin_panel),
    path('manage-users/<link_tag>/<department>/<user_id>/', manage_users),
    path('incidents-list/<clicked_from>/<get_user>/<incident_status>/', incidents_list),
    path('department-incidents/<clicked_from>/<get_user>/<incident_status>/', department_incidents),
    path('incident-type/<get_user>/<incident_type>/<clicked_from>/', incidents_types),
    path('department-incident-type/<get_user>/<incident_type>/<clicked_from>/', department_incidents_types),

    url(r'^media/(?P<path>.*)$', serve,{'document_root':       settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]
