from django.shortcuts import render
from .models import IncidencesTable, CountyDepartments, CountyUsers, IncidentStatus, Feedback, AuthLevel
from django.db import connection
from django.http import HttpResponseRedirect
from .generate_reference_number import generate_first_reference_number, generate_new_reference_number
import datetime
from .security import SESSION_KEY, hash_password, hash_phrase
from django.contrib import messages
from .utils import not_null
from .utils import sendsms


def fetch_inserted_ref_no():
    with connection.cursor() as cursor:
        cursor.execute("SELECT ref_no FROM incidents_incidencestable order by id desc")
        row = cursor.fetchone()
    return row


def insert_function(request):
    try:
        if request.method == 'POST':
            new_name = request.POST.get('name_of')
            new_mail = request.POST.get('email_of')
            new_phone = request.POST.get('phone_of')
            new_gender = request.POST.get('gender_details')
            new_incident_type = request.POST.get('incident_type')
            new_location = request.POST.get('location')
            new_subcounty = request.POST.get('subcounty')
            new_ward = request.POST.get('wards')
            new_incident = request.POST.get('description')
            dept_selected = request.POST.get('department')
            now = datetime.datetime.now()
            date_string = now.strftime("%d/%m/%Y")
            current_time = now.strftime("%H:%M:%S")
            date_of_incident = f"{date_string}:{current_time}"
            status_load= IncidentStatus.objects.get(status_name='pending')
            department_insert= CountyDepartments.objects.get(department_name=dept_selected)
            inserted_ref_no = fetch_inserted_ref_no()
            dept_strip = dept_selected[: 3]
            # department_users= CountyUsers.objects.filter(countydepartments__)
            """the program will raise a ValueError when it tries to create reference number from the database
            output which will be 'None'."""
            try:
                generated_ref_no = generate_new_reference_number(inserted_ref_no, dept_strip)
            except Exception as er:
                generated_ref_no = generate_first_reference_number(dept_strip)

            db_inserter = IncidencesTable(ref_no=generated_ref_no,
                                        name_of_complainant=new_name,
                                        incident_type=new_incident_type,
                                        location=new_location,
                                        department=department_insert,
                                        description=new_incident,
                                        gender =new_gender,
                                        subcounty=new_subcounty,
                                        email_of_complainant=new_mail,
                                        phone_no=new_phone,
                                        incident_report_date=date_of_incident,
                                        wards=new_ward,
                                        status= status_load)
            db_inserter.save()
            sendsms(new_phone, generated_ref_no)
            messages.success(request, 'Submitted successfuly, your reference number is :' + generated_ref_no)
            return HttpResponseRedirect('/')
    except Exception as insert_error:
        messages.error(request, insert_error)
        return HttpResponseRedirect('/')


def add_department_back_end(request):
    try:
        if request.method =='POST':
            new_department = request.POST.get('department')
            insert_department = CountyDepartments(department_name=new_department.upper())
            insert_department.save()
            return HttpResponseRedirect(f'/add/{SESSION_KEY}')
    except Exception as department_error:
        messages.error(request, department_error)
        return HttpResponseRedirect(f'/add/{SESSION_KEY}')


def registration_back_end(request):
    if request.method == 'POST':
        new_user_name = request.POST.get('user_name')
        new_user_mail = request.POST.get('user_mail')
        new_user_department = request.POST.get('department')
        user_department= CountyDepartments.objects.get(department_name=new_user_department)
        new_user_pass = request.POST.get('user_pass')
        user_status= request.POST.get('group')
        user_group = AuthLevel.objects.get(name=user_status)
        if user_status=='department officer':
            user_status=False
        else:
            user_status=True
        generate_pass = hash_password(new_user_name, new_user_pass)
        register_user= CountyUsers(user_name=new_user_name,
                                   user_mail=new_user_mail,
                                   salt_value= hash_phrase(new_user_name),
                                   department= user_department,
                                   level = user_group,
                                   user_pass=generate_pass,
                                   is_admin=user_status)
        register_user.save()
        return HttpResponseRedirect('/login/')


def change_user(request):
        if request.method == 'POST':
            new_user_name = request.POST.get('user_name')
            admin_user = request.POST.get('admin')
            new_user_mail = request.POST.get('user_mail')
            new_user_department = request.POST.get('department')
            user_status= request.POST.get('admin_status')
            delete_user= request.POST.get('delete_user')
            change_user= CountyUsers.objects.filter(user_name= new_user_name)
            if delete_user == 'delete':
                change_user.delete()
            else:
                if user_status=='admin':
                    user_status=True
                else:
                    user_status=False
                change_user.is_admin = user_status
                change_user.save()
            return HttpResponseRedirect('/admin-dashboard/{}/{}/'.format(admin_user, SESSION_KEY))


def assign_user_incident(request):
    try:
        if request.method == 'POST':
            incident_id= request.POST.get('incident_id')
            username= request.POST.get('user_assigned')
            get_user = request.POST.get('user')
            get_status= request.POST.get('status')
            send_to_user= request.POST.get('external')
            user_feedback = request.POST.get('feedback')
            link_clicked = request.POST.get('link-from')
            user = CountyUsers.objects.get(id=int(get_user))
            new_assignment= IncidencesTable.objects.get(id=int(incident_id))
            if not_null(get_status):
                new_status = IncidentStatus.objects.get(status_name=get_status)
                new_assignment.status= new_status
                new_assignment.save()
                messages.success(request, "You changed incident status to complete")
                return HttpResponseRedirect(f'/{link_clicked}/{user.user_name}/{SESSION_KEY}')
            if not_null(username):
                user_assigned= CountyUsers.objects.get(user_name= username)
                new_status= IncidentStatus.objects.get(status_name='assigned')
                new_assignment.assigned_to.add(user_assigned)
                new_assignment.status = new_status
                new_assignment.save()
                messages.success(request, f"You have successfully assigned incident to {user_assigned.user_name}")
                return HttpResponseRedirect(f'/{link_clicked}/{user.user_name}/{SESSION_KEY}')
            if not_null(send_to_user):
                feedback = Feedback(user=user, reply= user_feedback)
                feedback.save()
                feedback.incident.add(new_assignment)
                sendsms(new_assignment.phone, user_feedback)
                messages.success(request, "Your feedback has beensent to the reporter")
                return HttpResponseRedirect(f'/{link_clicked}/{user.user_name}/{SESSION_KEY}')
            if not_null(user_feedback):
                feedback = Feedback(user=user, reply= user_feedback)
                feedback.save()
                feedback.incident.add(new_assignment)
                addressed = IncidentStatus.objects.get(status_name='addressed')
                new_assignment.status = addressed
                new_assignment.save()
                messages.success(request, "You have successfully submitted your feedback")
                return HttpResponseRedirect(f'/{link_clicked}/{user.user_name}/{SESSION_KEY}')
            messages.error(request, "You did not perform any action")
            return HttpResponseRedirect(f'/{link_clicked}/{user.user_name}/{SESSION_KEY}')
    except Exception as insert_error:
        messages.error(request, insert_error +",Try again")
        return HttpResponseRedirect(f'/{link_clicked}/{user.user_name}/{SESSION_KEY}')

