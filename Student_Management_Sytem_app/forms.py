from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.forms import Form
from Student_Management_Sytem_app.models import Courses, SessionYearModel


class DateInput(forms.DateInput):
    input_type = "date"


class AddStudentForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class": "form-control"}))
    password = forms.CharField(label="Password", max_length=50,
                               widget=forms.PasswordInput(attrs={"class": "form-control"}))
    renter_password = forms.CharField(label="re-enter Password", max_length=50,
                               widget=forms.PasswordInput(attrs={"class": "form-control"}))
    first_name = forms.CharField(label="First Name", max_length=50,
                                 widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(label="Last Name", max_length=50,
                                widget=forms.TextInput(attrs={"class": "form-control"}))
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}))
    address = forms.CharField(label="Address", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}))

    # For Displaying Courses
    try:
        courses = Courses.objects.all()
        course_list = []
        for course in courses:
            single_course = (course.id, course.course_name)
            course_list.append(single_course)
    except:
        course_list = []

    # For Displaying Session Years
    try:
        session_years = SessionYearModel.objects.all()
        session_year_list = []
        for session_year in session_years:
            single_session_year = (
            session_year.id, str(session_year.session_start_year) + " to " + str(session_year.session_end_year))
            session_year_list.append(single_session_year)
            print(session_year.session_start_year)
    except:
        session_year_list = []

    gender_list = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )

    course_id = forms.ChoiceField(label="Course", choices=course_list,
                                  widget=forms.Select(attrs={"class": "form-control"}))
    gender = forms.ChoiceField(label="Gender", choices=gender_list,
                               widget=forms.Select(attrs={"class": "form-control"}))
    session_year_id = forms.ChoiceField(label="Session Year", choices=session_year_list,
                                        widget=forms.Select(attrs={"class": "form-control"}))
    # session_start_year = forms.DateField(label="Session Start", widget=DateInput(attrs={"class":"form-control"}))
    # session_end_year = forms.DateField(label="Session End", widget=DateInput(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label="Profile Pic", required=False,
                                  widget=forms.FileInput(attrs={"class": "form-control"}))
    def clean(self):
        cd=self.cleaned_data
        password=cd.get("password")
        renter_passwrd=cd.get("renter_password")
        if password != renter_passwrd:
            raise ValidationError("passwords didnot match")

        return cd


class EditStudentForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class": "form-control"}))
    first_name = forms.CharField(label="First Name", max_length=50,
                                 widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(label="Last Name", max_length=50,
                                widget=forms.TextInput(attrs={"class": "form-control"}))
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}))
    address = forms.CharField(label="Address", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}))

    # For Displaying Courses
    try:
        courses = Courses.objects.all()
        course_list = []

        for course in courses:

            single_course = (course.id, course.course_name)
            course_list.append(single_course)
    except:
        course_list = []

    # For Displaying Session Years
    try:
        session_years = SessionYearModel.objects.all()
        session_year_list = []
        for session_year in session_years:
            single_session_year = (
            session_year.id, str(session_year.session_start_year) + " to " + str(session_year.session_end_year))
            session_year_list.append(single_session_year)

    except:
        session_year_list = []

    gender_list = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )

    course_id = forms.ChoiceField(label="Course", choices=course_list,
                                  widget=forms.Select(attrs={"class": "form-control"}))
    gender = forms.ChoiceField(label="Gender", choices=gender_list,
                               widget=forms.Select(attrs={"class": "form-control"}))
    session_year_id = forms.ChoiceField(label="Session Year", choices=session_year_list,
                                        widget=forms.Select(attrs={"class": "form-control"}))
    # session_start_year = forms.DateField(label="Session Start", widget=DateInput(attrs={"class":"form-control"}))
    # session_end_year = forms.DateField(label="Session End", widget=DateInput(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label="Profile Pic", required=False,
                                  widget=forms.FileInput(attrs={"class": "form-control"}))

'''class ReportCardForm(forms.Form):
      student_reportcard=forms.FileField(label="Profile Pic", required=False,
                                  widget=forms.FileInput(attrs={"class": "form-control"}))'''

class MyForm(forms.Form):
    original_field=forms.CharField()
    extra_field_count=forms.CharField(widget=forms.HiddenInput)

    def __init__(self,*args,**kwargs):
         extra_fields=kwargs.pop('extra',0)
         super(MyForm,self).__init__(*args,**kwargs)
         self.fields['extra_field_count'].initial=extra_fields

         for index in range(int(extra_fields)):
             self.fields['extra_field_{index}'.format(index=index)]=forms.CharField()

class ReportCardForm(forms.Form):
      session= forms.CharField(label="session", max_length=50,
                                widget=forms.TextInput(attrs={"class": "form-control"}))
      exam_type=forms.CharField(label="Last Name", max_length=50,
                                widget=forms.TextInput(attrs={"class": "form-control"}))
      username=forms.CharField(label="Last Name", max_length=50,
                                widget=forms.TextInput(attrs={"class": "form-control"}))
      student_name=forms.CharField(label="Last Name", max_length=50,
                                widget=forms.TextInput(attrs={"class": "form-control"}))
      class_teacher=forms.CharField(label="Last Name", max_length=50,
                                widget=forms.TextInput(attrs={"class": "form-control"}))
      subjects=forms.CharField(label="Last Name", max_length=50,
                                widget=forms.TextInput(attrs={"class": "form-control"}))
      full_Mark=forms.CharField(label="Last Name", max_length=50,
                                widget=forms.TextInput(attrs={"class": "form-control"}))
      pass_mark=forms.CharField(label="Last Name", max_length=50,
                      widget=forms.TextInput(attrs={"class": "form-control"}))
      mark_obtained=forms.CharField(label="Last Name", max_length=50,
                                widget=forms.TextInput(attrs={"class": "form-control"}))

class SessionExamtypeForm(forms.Form):
    try:
        session_years = SessionYearModel.objects.all()
        session_year_list = []
        for session_year in session_years:
            single_session_year = (
                session_year.id, str(session_year.session_start_year) + " to " + str(session_year.session_end_year))
            session_year_list.append(single_session_year)

    except:
        session_year_list = []

    exam_list = (
        ('ANNUAL', 'ANNUAL'),
        ('HALF-YEARLY', 'HALF YEARLY'),
        ('TEST','TEST')
    )
    examtype = forms.ChoiceField(label="Exam", choices=exam_list,
                                  widget=forms.Select(attrs={"class": "form-control"}))

    session_year_id = forms.ChoiceField(label="Session Year", choices=session_year_list,
                                        widget=forms.Select(attrs={"class": "form-control"}))




'''NUMS= [
    ('Student', 'Student'),
    ('Teacher', 'Teacher'),
    ('Admin', 'Admin'),
      ]


class CHOICES(forms.Form):
    NUMS = forms.CharField(widget=forms.RadioSelect(choices=NUMS))'''