from django.db import models
import django


class CountyDepartments(models.Model):
	department_name= models.CharField(max_length=100, unique=True)

	def __str__(self):
		return f"{self.id},{self.department_name}"


class IncidentStatus(models.Model):
	status_name = models.CharField(max_length=50, unique=True)

	def __str__(self):
		return f"{self.id},{self.status_name}"

class AuthLevel(models.Model):
	name = models.CharField(max_length=50, unique=True)

class CountyUsers(models.Model):
	user_name = models.CharField(max_length=100)
	user_mail = models.EmailField(max_length=150)
	salt_value = models.CharField(max_length=500)
	department=models.ForeignKey(CountyDepartments, on_delete=models.DO_NOTHING)
	level = models.ForeignKey(AuthLevel, on_delete=models.DO_NOTHING)
	user_pass = models.CharField(max_length=500)
	is_admin = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.user_name},{self.department_id},{self.user_pass},{self.salt_value},{self.is_admin}"



class IncidencesTable(models.Model):
	ref_no         = models.CharField(unique=True, max_length=50)
	name_of_complainant = models.CharField(max_length=25, default='Anonymous')
	incident_type  = models.CharField(max_length=25)
	location       = models.CharField(max_length=25, blank=True)
	department     = models.ForeignKey(CountyDepartments, on_delete=models.DO_NOTHING)
	description    = models.TextField(max_length=1000)
	gender = models.CharField(max_length=10)
	subcounty      = models.CharField(max_length=20, default='Not Specified',blank=True)
	wards          = models.CharField(max_length=25, blank=True)
	email_of_complainant= models.CharField(max_length=50, blank=True)
	phone_no = models.CharField(max_length=15, blank=True)
	incident_report_date = models.CharField(max_length=50)
	incident_occurrence_date= models.DateField(blank=True, default= django.utils.timezone.now)
	status = models.ForeignKey(IncidentStatus, on_delete=models.DO_NOTHING)
	assigned_to= models.ManyToManyField(CountyUsers)

	def __str__(self):
		return f"{self.ref_no},{self.department_id}"

	class Meta:
		ordering= ['-incident_occurrence_date']

class Feedback(models.Model):
	incident = models.ManyToManyField(IncidencesTable)
	user = models.ForeignKey(CountyUsers, on_delete=models.DO_NOTHING)
	reply = models.CharField(max_length=1000, blank=False)
	date_of_reply = models.DateTimeField(default=django.utils.timezone.now)

