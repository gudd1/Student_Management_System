import math
from random import random

from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db.models import Q
from django.shortcuts import render
#from channels.auth import login, logout
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages

from Student_Management_Sytem_app.EmailBackEnd import EmailBackEnd
#from Student_Management_Sytem_app.forms import CHOICES
from Student_Management_Sytem_app.models import CustomUser, Staffs
from Student_Management_Sytem_app.OTPverification import TOTPVerification

def index(request):
    return render(request, 'index.html')


def home(request):
    return render(request, 'home.html')


def register(request):
    '''form = CHOICES(request.POST)

    if form.is_valid():
        selected = form.cleaned_data.get("NUMS")
        print(selected)'''
    return render(request,'register.html')


def DoRegister(request):
    print("ref")
    if request.method != 'POST':
       return HttpResponse("<h2> Mathod not Allowed!</h2>")
    else:


       Email = request.POST['E-mail']
       try:
           validate_email(Email)
       except ValidationError:
           messages.error(request, 'enter valid email')
       if (CustomUser.objects.filter(Q(email=request.POST['username']))):
          messages.error(request, 'ID already registered!')
       else:
          if request.POST['Password'] != request.POST['Re-password']:
             messages.error(request, 'passwords did not match')
          else:
             if (CustomUser.objects.filter(Q(email=Email))):
                messages.error(request, 'E-mail already exist')
             else:
                id=request.POST['username']
                if id.find("sems")==-1:
                    messages.error(request,'Invalid ID')
                else:
                    user = CustomUser.objects.create_user(username=request.POST['username'],password=request.POST['Password'],
                                                      email=Email,
                                                      first_name=request.POST['first_name'],
                                                      last_name=request.POST['last_name'], user_type=1)

                    user.save()
                    messages.success(request,'Registered Successfully!')
                    return redirect('login')


       return render(request,'register.html')





def reset_password(request):
    return render(request,'password_reset_form.html')
def otp_request(request):
    if request.method == 'POST':
       Email = request.POST.get('E-mail')
       print("here")
       try:
          validate_email(Email)


          if (CustomUser.objects.filter(email=Email)):
              OTP=TOTPVerification()
              print("generate_otp")

              print(OTP.key,OTP.time)
              o=OTP.key
              htmlgen = '<p>Your OTP is :<strong>' + str(
                  o) + '</strong></p> <p>Expires in :<strong> 10 minutes</strong>'
              try:
                  send_mail('OTP Request', 'your otp is:' + str(o), 'production.sems@example.com',[Email],fail_silently=False, html_message=htmlgen)


              except:
                  return HttpResponse('Invalid header found.')
              print("sent")


              obj={}
              obj['key']=OTP.key+" "+str(OTP.time)+" "+Email
              obj['time']=OTP.time
              obj['Email']=Email
              #return redirect('otp_varification')
              return render(request,'otp_varification.html', obj)
          else:
              messages.error(request, 'E-mail address not registered!')
              return redirect('reset_password')
       except ValidationError:
          messages.error(request, 'enter valid email address')
          return redirect('reset_password')
    else:
        return HttpResponse("<h2>Method Not Allowed</h2>")

def otp_varification(request):
    print("how?")

    '''context = {
        "key": key,
        "time":time,
        "Email":Email
    }'''

    return render(request,'otp_varification.html')
def verify_otp(request,key):
    print("it came here")
    print(key)
    s=key.split()
    print(s[0])
    key=int(s[0])
    time=float(s[1])
    Email=s[2]
    print("verify_Otp")
    if request.method=="POST":
        OTP=TOTPVerification()

        valid=OTP.verify_key(key,time,request.POST["OTP"])

        print("verify")
        if valid==True:
            print("verified")
            obj={
                "Email":Email
            }

            return render(request,'new_password.html',obj)
        else:
            messages.error(request,OTP.error)
            obj = {}
            obj['key'] = str(key) + " " + str(time) + " " + Email
            return render(request,'otp_varification.html',obj)
    else:
        return HttpResponse("<h2>Method Not Allowed</h2>")
def new_password(request):
    context={
        "user":"user"
    }
    return render(request,'new_password.html')
def save_password(request,Email):


    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        if request.POST['Password1'] != request.POST['Password2']:
            messages.error(request, 'Entries did not match')
            obj={ "Email":Email}
            return render(request,'new_password.html',obj)
        else:
            password=request.POST.get('Password1')
            User=CustomUser.objects.get(email=Email)
            try:
              User.set_password(password)
              User.save()
            except:
              return HttpResponse("<h2>Failed!</h2>")
            messages.success(request,'Password changed Sueccessfully')
            return redirect('login')



def loginPage(request):
    return render(request, 'login.html')


def doLogin(request):


    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:


        user = EmailBackEnd.authenticate(request, username=request.POST.get('email'),
                                         password=request.POST.get('password'))
        if user != None:
            login(request, user)
            user_type = user.user_type
            # return HttpResponse("Email: "+request.POST.get('email')+ " Password: "+request.POST.get('password'))
            if user_type == '1':
                return redirect('admin_home')

            elif user_type == '2':
                # return HttpResponse("Staff Login")
                return redirect('staff_home')

            elif user_type == '3':
                # return HttpResponse("Student Login")
                return redirect('student_home')
            else:
                messages.error(request, "Invalid Login!")
                return redirect('login')
        else:
            messages.error(request, "Invalid Login Credentials!")
            # return HttpResponseRedirect("/")
            return redirect('login')


def get_user_details(request):
    if request.user != None:
        return HttpResponse("User: " + request.user.email + " User Type: " + request.user.user_type)
    else:
        return HttpResponse("Please Login First")


def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')

# Create your views here.
