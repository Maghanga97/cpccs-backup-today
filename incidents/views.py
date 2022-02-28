from django.shortcuts import get_list_or_404, render
from .models import IncidencesTable, CountyDepartments, CountyUsers, IncidentStatus, Feedback, AuthLevel
from django.http import HttpResponseRedirect, HttpResponse
from .security import authenticated, SESSION_KEY
from django.contrib import messages
from .utils import render_to_pdf
from django.template.loader import get_template
from .utils import not_null


def incidents_view(request):
    departments = CountyDepartments.objects.all()
    incidents_context = {'departments': departments}
    return render(request, 'home.html', incidents_context)


def add_department(request, dept_session_key=None):
    if dept_session_key == SESSION_KEY:
        return render(request, 'base_admin/department-registration.html', {})
    else:
        return HttpResponse("You need authorization from a registered user")


def registration_view(request, reg_session_key=None):
    if reg_session_key == SESSION_KEY:
        departments =CountyDepartments.objects.all()
        levels = AuthLevel.objects.all()
        return render(request, 'base_admin/register-admin.html', {'departments': departments, 'levels':levels})
    else:
        return HttpResponse("You need authorization from a registered user")


def login(request):
    try:
        if request.method== 'POST':
            requesting_user = request.POST.get('username')
            requesting_user_password= request.POST.get('password')
            user_authentication= authenticated(requesting_user, requesting_user_password)
            try:
                if user_authentication == True:
                    user = CountyUsers.objects.get(user_name=requesting_user)
                    if user.level.name == 'super admin' :
                        return HttpResponseRedirect(f'/main-dashboard/{requesting_user}/{SESSION_KEY}/')
                    return HttpResponseRedirect(f'/admin-dashboard/{requesting_user}/{SESSION_KEY}/')
                else:
                    messages.error(request, user_authentication)
                    return HttpResponseRedirect('/login/')
            except Exception as login_error:
                messages.error(request, login_error)
                return HttpResponseRedirect('/login/')
    except Exception as first_login_error:
                messages.error(request, first_login_error)
                return HttpResponseRedirect('/login/')
    return render(request, 'base_admin/login.html', {})


def admin_view(request, user, session):
    if session == SESSION_KEY:
        get_user= CountyUsers.objects.get(user_name=user)
        get_department_id =get_user.department.id
        get_department = CountyDepartments.objects.get(id=get_department_id)
        filtered_incident_data = IncidencesTable.objects.filter(department=get_department)
        display_incidents = filtered_incident_data[:10]
        get_user_admin_status = get_user.is_admin
        pending= IncidentStatus.objects.get(status_name='pending')
        assigned= IncidentStatus.objects.get(status_name='assigned')
        completed= IncidentStatus.objects.get(status_name='completed')
        total_filtered_incidents = filtered_incident_data.count()
        pending_incidents = filtered_incident_data.filter(status=pending).count()
        number_of_incidents_completed = filtered_incident_data.filter(status=completed).count()
        number_of_incidents_assigned = filtered_incident_data.filter(status=assigned).count()
        incidents_assigned = filtered_incident_data.filter(status=assigned)
        incidents_pending = filtered_incident_data.filter(status=pending)
        completed_incidents = filtered_incident_data.filter(status=completed)
        incidents_assigned_to_user = filtered_incident_data.filter(status=assigned, assigned_to=get_user)
        display_incidents_assigned_to_user = incidents_assigned_to_user[:10]
        incidents_completed_by_user = filtered_incident_data.filter(status=completed, assigned_to=get_user)
        number_of_incidents_completed_by_user = filtered_incident_data.filter(status=completed, assigned_to=get_user).count()
        number_of_incidents_assigned_to_user= filtered_incident_data.filter(status=assigned, assigned_to=get_user).count()
        users =CountyUsers.objects.filter(department_id=get_department)
        number_of_users= users.count()
        admin_context={'user': get_user,
                        "link_tag": "admin-dashboard",
                        'user_details': get_user_admin_status,
                        'users':number_of_users,
                        'user_list': users,
                        'session' : SESSION_KEY,
                        'pending': pending_incidents,
                        'completed': number_of_incidents_completed,
                        'incidents': display_incidents,
                        'assigned' : number_of_incidents_assigned,
                        'assigned_to_admin': incidents_assigned_to_user,
                        'incidents_count': total_filtered_incidents}
        user_context= {'user': get_user, 'assigned': number_of_incidents_assigned_to_user, 'link_tag': 'admin-dashboard',
                        'session': SESSION_KEY,
                        'completed': number_of_incidents_completed_by_user,
                        'incidents': incidents_assigned_to_user,
                        'display_incidents': display_incidents_assigned_to_user }

        if get_user_admin_status == True:
            return render(request,'base_admin/department-admin.html',admin_context)
        else:
            return render(request,'base_admin/department.html',user_context)
    else:
        return HttpResponse("Login required")

def main_admin_panel(request, user, session):
    if session == SESSION_KEY:
        department = request.GET.get('department')
        search = request.GET.get('search')
        view_incidents = IncidencesTable.objects.all()
        display_incidents = IncidencesTable.objects.all()[:10]
        users = CountyUsers.objects.all()
        if not_null(department):
            view_incidents= view_incidents.filter(department_id=int(department))
            display_incidents = IncidencesTable.objects.filter(department_id= int(department))[:10]
            users= users.filter(department_id=int(department))
        # if not_null(search):
        #     view_incidents = view_incidents.get(ref_no=search)
        #     department = view_incidents.department.id
        #     users = users.filter(department_id= department)
        assigned= IncidentStatus.objects.get(status_name='assigned')
        completed = IncidentStatus.objects.get(status_name= 'completed')
        pending = IncidentStatus.objects.get(status_name= 'pending')
        completed_incidents= view_incidents.filter(status=completed)
        assigned_incidents = view_incidents.filter(status=assigned)
        pending_incidents = view_incidents.filter(status=pending)
        completed_count = completed_incidents.count()
        pending_count = pending_incidents.count()
        user = CountyUsers.objects.get(user_name= user)
        assigned_count= assigned_incidents.count()
        count_incidents = view_incidents.count()
        departments = CountyDepartments.objects.all()
        number_of_departments = departments.count()
        number_of_users= users.count()
        return render(request, 'base_admin/main.html',{'incidents': display_incidents,
                                                                    'count_incidents': count_incidents,
                                                                    'dep_count': number_of_departments,
                                                                    'departments': departments,
                                                                    'completed_count': completed_count,
                                                                    'pending_count': pending_count,
                                                                    'assigned_count' : assigned_count,
                                                                    'users': users,
                                                                    'user': user,
                                                                    'session': SESSION_KEY,
                                                                    'number_of_users': number_of_users})
    else:
        messages.error(request, 'Unauthorised access')
        return HttpResponseRedirect('/login/')


def details(request, clicked_from, user, incident):
    get_incident= incident
    get_user = user
    incident= IncidencesTable.objects.get(id=int(get_incident))
    user = CountyUsers.objects.get(id=int(get_user))
    department= incident.department.id
    get_users= CountyUsers.objects.filter(department_id=department)
    feedback = Feedback.objects.filter(incident=incident)
    return render(request, 'base_admin/details.html', {'details': incident,'user': user, 'session': SESSION_KEY, 'feedback': feedback, 'users': get_users, 'status': incident.status.status_name, 'link_tag': clicked_from})

def incidents_list(request, clicked_from, get_user, incident_status):
    status = IncidentStatus.objects.get(status_name = incident_status)
    incidents = IncidencesTable.objects.filter(status = status)
    user = CountyUsers.objects.get(id=int(get_user))
    return render(request, 'base_admin/main-incidents.html', {'incidents': incidents,'user': user, 'session': SESSION_KEY, 'link_tag': clicked_from})

def incidents_types(request, clicked_from, get_user, incident_type):
    incidents = IncidencesTable.objects.filter(incident_type = incident_type)
    user = CountyUsers.objects.get(id=int(get_user))
    return render(request, 'base_admin/main-incidents.html', {'incidents': incidents,'user': user, 'session': SESSION_KEY, 'link_tag': clicked_from})


def department_incidents_types(request, clicked_from, get_user, incident_type):
    user = CountyUsers.objects.get(id=int(get_user))
    department = CountyDepartments.objects.get(id = int(user.department.id))
    incidents = IncidencesTable.objects.filter(incident_type = incident_type, department=department)
    return render(request, 'base_admin/incidents.html', {'incidents': incidents,'user': user, 'session': SESSION_KEY, 'link_tag': clicked_from})


def department_incidents(request, clicked_from, get_user, incident_status):
    user = CountyUsers.objects.get(id=int(get_user))
    department = CountyDepartments.objects.get(id = int(user.department.id))
    status = IncidentStatus.objects.get(status_name = incident_status)
    incidents = IncidencesTable.objects.filter(status = status, department=department)
    return render(request, 'base_admin/incidents.html', {'incidents': incidents,'user': user, 'session': SESSION_KEY, 'link_tag': clicked_from})


def edit_user_view(request, admin, user_id, clicked_from):
    user = CountyUsers.objects.get(id=user_id)
    return render(request, 'base_admin/edit-user.html', {'user': user, 'admin_user' : admin, 'link_tag': clicked_from})

def manage_users(request,link_tag, department, user_id):
    user = CountyUsers.objects.get(id=int(user_id))
    if department == "All":
        users = CountyUsers.objects.all()
        return render(request, 'base_admin/all-users.html', {'users': users, 'user' : user, 'session': SESSION_KEY, 'link_tag': link_tag})
    else:
        users_department = CountyDepartments.objects.get(id=int(department))
        users = CountyUsers.objects.filter(department=users_department)
        return render(request, 'base_admin/manage-users.html', {'user' : user, 'users': users, 'session': SESSION_KEY, 'link_tag': link_tag})




def incident_pdf(request,reference ):
        template = get_template('base_admin/report.html')
        incident = IncidencesTable.objects.get(id=reference)
        context= {'incident': incident}
        html = template.render(context)
        pdf = render_to_pdf('base_admin/report.html', context)
        # return HttpResponse(pdf, content_type='application/pdf')
        return pdf

def overall_report(request):
        template = get_template('base_admin/general-report.html')
        incident = IncidencesTable.objects.all()
        context= {'incidents': incident}
        html = template.render(context)
        pdf = render_to_pdf('base_admin/general-report.html', context)
        # return HttpResponse(pdf, content_type='application/pdf')
        return pdf

try:
    pending= IncidentStatus(status_name='pending')
    completed = IncidentStatus(status_name= 'completed')
    assigned = IncidentStatus(status_name = 'assigned')
    addressed = IncidentStatus(status_name = 'addressed')
    addressed.save()
    pending.save()
    completed.save()
    assigned.save()
except Exception as initial_error:
    pass

try:
    water = CountyDepartments(department_name='WATER AND IRRIGATION')
    finance = CountyDepartments(department_name='FINANCE AND PLANNING')
    education = CountyDepartments(department_name='EDUCATION AND LIBRARIES')
    health = CountyDepartments(department_name='HEALTH SERVICES')
    youth = CountyDepartments(department_name='YOUTH,GENDER,SPORT AND SOCIAL SERVICES')
    agriculture = CountyDepartments(department_name='AGRICULTURE,LIVESTOCK AND FISHERIES')
    works = CountyDepartments(department_name='PUBLIC WORKS, HOUSING AND INFRASTRUCTURE')
    lands = CountyDepartments(department_name='LANDS, ENVIRONMENT AND NATURAL RESOURCES')
    trade = CountyDepartments(department_name='TRADE, TOURISM AND COOPERATIVE DEVELOPMENT')
    service= CountyDepartments(department_name='PUBLIC SERVICE AND ADMINISTRATION')
    mining = CountyDepartments(department_name='PORTFOLIO OF MINING, INDUSTRIALISATION, ICT AND SPECIAL PROGRAMMES')
    agriculture.save()
    education.save()
    finance.save()
    health.save()
    lands.save()
    mining.save()
    service.save()
    works.save()
    trade.save()
    water.save()
    youth.save()
except Exception as create_deps:
    pass

