from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage  # To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json

from Student_Management_Sytem_app.forms import ReportCardForm, MyForm, AddStudentForm, SessionExamtypeForm
from Student_Management_Sytem_app.models import CustomUser, Staffs, Courses, Subjects, Students, SessionYearModel, \
    Attendance, \
    AttendanceReport, LeaveReportStaff, FeedBackStaffs, StudentResult, StudentsResult



def staff_home(request):
    staff_count = Staffs.objects.all().count()
    course_count = Courses.objects.all().count()
    # Fetching All Students under Staff

    subjects = Subjects.objects.filter(staff_id=request.user.id)
    course_id_list = []
    for subject in subjects:
        course = Courses.objects.get(id=subject.course_id.id)
        course_id_list.append(course.id)

    final_course = []
    # Removing Duplicate Course Id
    for course_id in course_id_list:
        if course_id not in final_course:
            final_course.append(course_id)

    students_count = Students.objects.filter(course_id__in=final_course).count()
    subject_count = subjects.count()

    # Fetch All Attendance Count
    attendance_count = Attendance.objects.filter(subject_id__in=subjects).count()
    # Fetch All Approve Leave
    staff = Staffs.objects.get(admin=request.user.id)
    leave_count = LeaveReportStaff.objects.filter(staff_id=staff.id, leave_status=1).count()

    # Fetch Attendance Data by Subjects
    subject_list = []
    attendance_list = []
    for subject in subjects:
        attendance_count1 = Attendance.objects.filter(subject_id=subject.id).count()
        subject_list.append(subject.subject_name)
        attendance_list.append(attendance_count1)

    students_attendance = Students.objects.filter(course_id__in=final_course)
    student_list = []
    student_list_attendance_present = []
    student_list_attendance_absent = []
    for student in students_attendance:
        attendance_present_count = AttendanceReport.objects.filter(status=True, student_id=student.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(status=False, student_id=student.id).count()
        student_list.append(student.admin.first_name + " " + student.admin.last_name)
        student_list_attendance_present.append(attendance_present_count)
        student_list_attendance_absent.append(attendance_absent_count)

    context = {
        "students_count": students_count,
        "attendance_count": attendance_count,
        "leave_count": leave_count,
        "subject_count": subject_count,
        "subject_list": subject_list,
        "attendance_list": attendance_list,
        "student_list": student_list,
        "attendance_present_list": student_list_attendance_present,
        "attendance_absent_list": student_list_attendance_absent,
        "staff_count": staff_count,
        "course_count": course_count
    }
    return render(request, "staff_template/staff_home_template.html", context)


def staff_list(request):
    print(request.method)
    staffs = Staffs.objects.all()
    print(staffs)
    context = {
        "staffs": staffs
    }

    return render(request, "staff_template/staffs_list.html",context)


def course_list(request):
    courses = Courses.objects.all()
    context = {
        "courses": courses
    }
    return render(request, 'staff_template/course_list.html', context)


def staff_take_attendance(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "staff_template/take_attendance_template.html", context)


def staff_apply_leave(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    leave_data = LeaveReportStaff.objects.filter(staff_id=staff_obj)
    context = {
        "leave_data": leave_data
    }
    return render(request, "staff_template/staff_apply_leave_template.html", context)


def staff_apply_leave_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_apply_leave')
    else:
        leave_date = request.POST.get('leave_date')
        leave_message = request.POST.get('leave_message')

        staff_obj = Staffs.objects.get(admin=request.user.id)
        try:
            leave_report = LeaveReportStaff(staff_id=staff_obj, leave_date=leave_date, leave_message=leave_message,
                                            leave_status=0)
            leave_report.save()
            messages.success(request, "Applied for Leave.")
            return redirect('staff_apply_leave')
        except:
            messages.error(request, "Failed to Apply Leave")
            return redirect('staff_apply_leave')


def staff_feedback(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    feedback_data = FeedBackStaffs.objects.filter(staff_id=staff_obj)
    context = {
        "feedback_data": feedback_data
    }
    return render(request, "staff_template/staff_feedback_template.html", context)


def staff_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('staff_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        staff_obj = Staffs.objects.get(admin=request.user.id)

        try:
            add_feedback = FeedBackStaffs(staff_id=staff_obj, feedback=feedback, feedback_reply="")
            add_feedback.save()
            messages.success(request, "Feedback Sent.")
            return redirect('staff_feedback')
        except:
            messages.error(request, "Failed to Send Feedback.")
            return redirect('staff_feedback')


# WE don't need csrf_token when using Ajax
@csrf_exempt
def get_students(request):
    # Getting Values from Ajax POST 'Fetch Student'
    subject_id = request.POST.get("subject")
    session_year = request.POST.get("session_year")

    # Students enroll to Course, Course has Subjects
    # Getting all data from subject model based on subject_id
    subject_model = Subjects.objects.get(id=subject_id)

    session_model = SessionYearModel.objects.get(id=session_year)

    students = Students.objects.filter(course_id=subject_model.course_id, session_year_id=session_model)

    # Only Passing Student Id and Student Name Only
    list_data = []

    for student in students:
        data_small = {"id": student.admin.id, "name": student.admin.first_name + " " + student.admin.last_name}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def save_attendance_data(request):
    # Get Values from Staf Take Attendance form via AJAX (JavaScript)
    # Use getlist to access HTML Array/List Input Data
    student_ids = request.POST.get("student_ids")
    subject_id = request.POST.get("subject_id")
    attendance_date = request.POST.get("attendance_date")
    session_year_id = request.POST.get("session_year_id")

    subject_model = Subjects.objects.get(id=subject_id)
    session_year_model = SessionYearModel.objects.get(id=session_year_id)

    json_student = json.loads(student_ids)
    # print(dict_student&#91;0]&#91;'id'])

    # print(student_ids)
    try:
        # First Attendance Data is Saved on Attendance Model
        attendance = Attendance(subject_id=subject_model, attendance_date=attendance_date,
                                session_year_id=session_year_model)
        attendance.save()

        for stud in json_student:
            # Attendance of Individual Student saved on AttendanceReport Model
            student = Students.objects.get(admin=stud['id'])
            attendance_report = AttendanceReport(student_id=student, attendance_id=attendance, status=stud['status'])
            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("Error")


def staff_update_attendance(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "staff_template/update_attendance_template.html", context)


@csrf_exempt
def get_attendance_dates(request):
    # Getting Values from Ajax POST 'Fetch Student'
    subject_id = request.POST.get("subject")
    session_year = request.POST.get("session_year_id")

    # Students enroll to Course, Course has Subjects
    # Getting all data from subject model based on subject_id
    subject_model = Subjects.objects.get(id=subject_id)

    session_model = SessionYearModel.objects.get(id=session_year)

    # students = Students.objects.filter(course_id=subject_model.course_id, session_year_id=session_model)
    attendance = Attendance.objects.filter(subject_id=subject_model, session_year_id=session_model)

    # Only Passing Student Id and Student Name Only
    list_data = []

    for attendance_single in attendance:
        data_small = {"id": attendance_single.id, "attendance_date": str(attendance_single.attendance_date),
                      "session_year_id": attendance_single.session_year_id.id}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def get_attendance_student(request):
    # Getting Values from Ajax POST 'Fetch Student'
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    # Only Passing Student Id and Student Name Only
    list_data = []

    for student in attendance_data:
        data_small = {"id": student.student_id.admin.id,
                      "name": student.student_id.admin.first_name + " " + student.student_id.admin.last_name,
                      "status": student.status}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def update_attendance_data(request):
    student_ids = request.POST.get("student_ids")

    attendance_date = request.POST.get("attendance_date")
    attendance = Attendance.objects.get(id=attendance_date)

    json_student = json.loads(student_ids)

    try:

        for stud in json_student:
            # Attendance of Individual Student saved on AttendanceReport Model
            student = Students.objects.get(admin=stud['id'])
            attendance_report = AttendanceReport.objects.get(student_id=student, attendance_id=attendance)
            attendance_report.status = stud['status']
            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("Error")


def staff_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    staff = Staffs.objects.get(admin=user)

    context = {
        "user": user,
        "staff": staff
    }
    return render(request, 'staff_template/staff_profile.html', context)


def staff_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('staff_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()

            staff = Staffs.objects.get(admin=customuser.id)
            staff.address = address
            staff.save()

            messages.success(request, "Profile Updated Successfully")
            return redirect('staff_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('staff_profile')


def staff_add_result(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    session_years = SessionYearModel.objects.all()
    courses = Courses.objects.all()

    for subject in subjects:
        print(subject.id, subject)
        '''if (subject.course_id):
           course=Courses.objects.filter(id=subject.course_id)
           courses.append(course.name)'''
    length=len(subjects)
    for course in courses:
        print(course.course_name)
    context = {
        "no":length,
        "courses": courses,
        "subjects": subjects,
        "session_years": session_years,
    }
    #return  render(request,"staff_template/make_report.html",context)
    return render(request, "staff_template/add_result_template.html", context)


def staff_add_result_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_add_result')
    else:
        student_admin_id = request.POST.get('student_list')
        assignment_marks = request.POST.get('assignment_marks')
        exam_marks = request.POST.get('exam_marks')
        subject_id = request.POST.get('subject')

        student_obj = Students.objects.get(admin=student_admin_id)
        subject_obj = Subjects.objects.get(id=subject_id)

        try:
            # Check if Students Result Already Exists or not
            check_exist = StudentResult.objects.filter(subject_id=subject_obj, student_id=student_obj).exists()
            if check_exist:
                result = StudentResult.objects.get(subject_id=subject_obj, student_id=student_obj)
                result.subject_assignment_marks = assignment_marks
                result.subject_exam_marks = exam_marks
                result.save()
                messages.success(request, "Result Updated Successfully!")
                return redirect('staff_add_result')
            else:
                result = StudentResult(student_id=student_obj, subject_id=subject_obj, subject_exam_marks=exam_marks,
                                       subject_assignment_marks=assignment_marks)
                result.save()
                messages.success(request, "Result Added Successfully!")
                return redirect('staff_add_result')
        except:
            messages.error(request, "Failed to Add Result!")
            return redirect('staff_add_result')


'''def student_report_card(request):
    print(request.get.id)

    return render(request, 'student_report_card.html')'''

def save_report_card(request):
    if request.method!="POST":
        return HttpResponse(request,"</h2> Invalid Method! </h2>")
    else:
        #ListFormSet=modelformset_factory(request,form=ListForm,extra=0)
        '''subject=request.POST.get("b")
        print(len(subject))
        for s in subject:
            print(s,"  ")'''
        print("Here_came")
        return redirect("save_report")

def save_report(request):
    form = ReportCardForm()
    context = {
        "form": form
    }
    return render(request, 'staff_template/make_report.html', context)

    #return render(request, "index.html")
@csrf_exempt
def take_input(request):
    print("its wrking")
    for key,value in request.session.items():
        print('{} => {}'.format(key,value))
    sum=[]
    subjects=request.POST.getlist("subjects[]")
    sum.append(subjects)
    fullmarks = request.POST.getlist("fullmarks[]")
    sum.append(fullmarks)
    passmarks = request.POST.getlist("passmarks[]")
    sum.append(passmarks)
    obtained= request.POST.getlist("obtained[]")
    sum.append(obtained)
    grades= request.POST.getlist("grade[]")
    sum.append(grades)
    student_name = request.session['student_name']
    sum.append(student_name)
    course = request.session['class']
    sum.append(course)
    teacher=request.POST.get("teacher_name")
    sum.append(teacher)
    year = request.session['year']
    student_id=CustomUser.objects.get(id=request.session['student_id'])
    course_id=Courses.objects.get(id=request.session['class_id'])
    session_yr_id=SessionYearModel.objects.get(id=request.session['session_yr_id'])
    exam_type=request.session['exam_type']
    student_userid = request.session['student_userid']
    create_primary_key = year + course + student_userid + exam_type
    id_exist=StudentsResult.objects.filter(id=create_primary_key).first()
    if id_exist==None:

       myModel=StudentsResult()
       myModel.id=create_primary_key
       myModel.myList=json.dumps(sum)
       myModel.student_id=student_id
       myModel.course_id=course_id
       myModel.session_year_id=session_yr_id
       myModel.test_type=exam_type
       myModel.teacher_id=request.session['_auth_user_id']
       myModel.save()
       print("saved!")
       return HttpResponse(True)
    else:
       id_exist.myList = json.dumps(sum)
       id_exist.student_id = student_id
       id_exist.course_id = course_id
       id_exist.session_year_id = session_yr_id
       id_exist.test_type = exam_type
       id_exist.teacher_id = request.session['_auth_user_id']
       id_exist.save()
       return HttpResponse(True)
    length=request.POST.get("length")
    length=int(length)
    print(length,length-1)
    teacher_name=request.session['teacher_name']




    '''student_id=request.session['student_id']
    print("student_id",student_id)'''
    #return HttpResponse("OK")
    print(year,course,student_userid)

    #print("key is :",create_primary_key)
    print(sum)
    object=StudentsResult.objects.filter(id=create_primary_key).first()
    if object!=None:
       print("obect id is: ",object.id)
    else:
        print("not saved")

    '''jsonDec=json.decoder.JSONDecoder()
        mypythonlist=jsonDec.decode(obj.myList)
        print('mypythonlist :',mypythonlist)
    or x in mypythonlist:
        print("list:")
        print(x)'''
    return HttpResponse(True)



def report_card(request):
    return render(request, "report_card.html")


def upload_report(request, student_id):
    Report_cardForm = ReportCardForm(request.POST, request.FILES)
    if Report_cardForm.is_valid():
        if len(request.FILES) != 0:
            report_card = request.FILES['report_card']
            fs = FileSystemStorage()
            filename = fs.save(report_card.name, report_card)
            report_card_url = fs.url(filename)
        else:
            report_card_url = None
        student_id = request.session.get('student_id')
        if student_id == None:
            user = CustomUser.objects.get(id=student_id)
            user.students.report_card = report_card_url
            user.save()


def student_report_card(request, student_id):
    request.session['student_id'] = student_id
    student = CustomUser.objects.get(id=student_id)
    print("student_id=",student_id,student)
    student_name=student.first_name+" "+student.last_name
    teacher_id = request.session['_auth_user_id']
    teacher = CustomUser.objects.get(id=teacher_id)

    course_id = request.session['class_id']

    course = Courses.objects.get(id=course_id)

    subjects = Subjects.objects.filter(course_id=course_id)
    # subject_admin_id=Subjects.objects.get(course_id=course_id)
    # session_yr_id=SessionYearModel.session_year_id

    # session_yr = SessionYearModel.objects.get(id=session_yr_id)

    # print(session_yr.session_start_year)
    session_yr_id=request.session["session_yr_id"]
    test=request.session['exam_type']

    print("form is valid",session_yr_id,test)
    session_yr = SessionYearModel.objects.get(id=session_yr_id)

    start_yr=session_yr.session_start_year.year
    end_yr=session_yr.session_end_year.year
    year=str(start_yr)+"-"+str(end_yr)
    print(year)

    teacher_name=teacher.first_name+" "+teacher.last_name
    request.session['teacher_name']=teacher_name
    request.session['year']=year
    request.session['student_name']=student_name
    request.session['student_userid']=student.username
    request.session['class']=course.course_name
    context = {
        "student_name":student_name,
       "year":year,
        "test":test,
       "student_id":student_id,
       "student": student,
       "teacher_name": teacher_name,
       "course": course,
       "subjects": subjects,

     }
    return render(request,"staff_template/make_report.html",context)
    #return render(request, "staff_template/student_report_card.html", context)

def session_examtype(request):
    print("inside sessin_examtype")
    form =SessionExamtypeForm()
    #examtypes={'annual':'ANNUAL','half_yearly':'HALF YEARLY','test':'TEST'}
    examtypes=["ANNUAL","HALF YEARLY","TEST"]
    session_years = SessionYearModel.objects.all()

    context = {
        "form":form,
        "examtype": examtypes,
        "session_years": session_years,

    }
    return render(request,"staff_template/session_examtype.html",context)

def class_list(request):
    print("inside class list")
    if request.method!="POST":
       return HttpResponse(request, "</h2> Invalid Method! </h2>")
    else:
       print("method is post")
       form = SessionExamtypeForm(request.POST)
       if form.is_valid():
          session_yr_id=form.cleaned_data.get('session_year_id')
          test=form.cleaned_data.get('examtype')
          request.session["session_yr_id"]=session_yr_id
          request.session['exam_type']=test
          print("here1")


          session_yr = SessionYearModel.objects.get(id=session_yr_id)
          print("here3")
          print(session_yr)
          start_yr = session_yr.session_start_year.year
          end_yr = session_yr.session_end_year.year
          year = str(start_yr) + "-" + str(end_yr)
          print(year)

          request.session['year'] = year

       '''print("form is valid",session_yr_id,test)
           session_yr = SessionYearModel.objects.get(id=session_yr_id)

           start_yr=session_yr.session_start_year.year
           end_yr=session_yr.session_end_year.year
           year=str(start_yr)+"-"+str(end_yr)
           print(year)'''
       form = MyForm()
       courses = Courses.objects.all()
       context = {
          'form': form,
          "courses": courses
       }
       return render(request, "staff_template/class_list.html", context)


def student_list(request, id):
    print("inside_student list")

    print(id)
    request.session['class_id'] = id
    students = Students.objects.filter(course_id=id)
    for student in students:
        print(student.admin.first_name)

    teacher_id = request.session['_auth_user_id']
    teacher = CustomUser.objects.get(id=teacher_id)
    print("sl1")
    course_id = request.session['class_id']
    print("sl2")
    course = Courses.objects.get(id=course_id)
    print("sl3")
    subjects = Subjects.objects.filter(course_id=course_id)
    print("sl4")

    test = request.session['exam_type']

    teacher_name = teacher.first_name + " " + teacher.last_name
    request.session['teacher_name'] = teacher_name
    request.session['class'] = course.course_name

    return render(request, 'staff_template/student_list.html', {'students': students})


@csrf_exempt
def check_ifsaved(request):
    print("iside check_ifsaved")
    if request.method=="POST":
       print(request.POST.get('student_id'))
       year = request.session['year']
       student_id = CustomUser.objects.get(id=request.POST.get('student_id'))

       course_id = Courses.objects.get(id=request.session['class_id'])

       exam_type = request.session['exam_type']
       student_userid = student_id.username
       course = request.session['class']
       create_primary_key = year + course + student_userid + exam_type
       print("key:",create_primary_key)
       id_exist = StudentsResult.objects.filter(id=create_primary_key).first()
       if id_exist != None:
          return HttpResponse(True)
       else:
           return HttpResponse(False)

@csrf_exempt
def delete_report(request):
    print ("inside_delete_report")
    year = request.session['year']
    student_id = CustomUser.objects.get(id=request.POST.get('student_id'))
    course_id = Courses.objects.get(id=request.session['class_id'])

    exam_type = request.session['exam_type']
    student_userid = student_id.username
    course = request.session['class']
    create_primary_key = year + course + student_userid + exam_type
    print(create_primary_key)
    id_exist = StudentsResult.objects.filter(id=create_primary_key).first()
    if id_exist != None:
       id_exist.delete()
       return HttpResponse(True)
    else:
       return  HttpResponse(False)


def edit_report_card(request,student_id):
    for key,value in request.session.items():
        print('{} => {}'.format(key,value))
    print("inside edit_report_card",student_id)

    student = CustomUser.objects.get(id=student_id)
    print("check1")
    student_name = student.first_name + " " + student.last_name
    year = request.session['year']
    print(year)
    print("check1.5")
    course_id = Courses.objects.get(id=request.session['class_id'])
    print("check2")

    exam_type = request.session['exam_type']
    print("check2.5")
    student_userid = student.username
    course = request.session['class']
    print("check2.7")
    create_primary_key = year + course + student_userid + exam_type
    print(create_primary_key)
    id_exist = StudentsResult.objects.filter(id=create_primary_key).first()
    print("check3")
    if id_exist != None:
        print("customer_exist")
        jsonDec = json.decoder.JSONDecoder()
        mypythonlist = jsonDec.decode(id_exist.myList)
        print('mypythonlist :', mypythonlist, len(mypythonlist))
        teacher_name = mypythonlist[7]
        course = mypythonlist[6]
        #student_name = student_id.first_name + " " + student_id.last_name
        subjects=mypythonlist[0]
        fullmarks=mypythonlist[1]
        passmarks=mypythonlist[2]
        obtained=mypythonlist[3]
        grades=mypythonlist[4]
        student_name=mypythonlist[5]
        maxlength=len(subjects)
        res= {}

        for i in range(maxlength):
            print(i,subjects[i])
            res[i]={}
            res[i]['subject']  =subjects[i]

            res[i]['fullmark']=fullmarks[i]
        print(res)
        pool=zip(subjects,fullmarks,passmarks,obtained,grades)
        context = {
            "pool":pool,
           "student_name": student_name,
           "year": year,
           "test": exam_type,
           "student_id": student_id,
           "student_userid": student_userid,
           "teacher_name": teacher_name,
           "course": course,
            "res":res,

           "subjects": subjects,
           "fullmarks" :fullmarks,
           "passmarks":passmarks,
           "obtained":obtained,
            "grades":grades,

        }

        return render(request,"staff_template/edit_report.html",context)
    else:
        print("customer doesnot exist")
    return render(request, "staff_template/edit_report.html")



@csrf_exempt
def edit_report(request):
    print ("inside_edit_report")
    student_id = CustomUser.objects.get(id=request.POST.get('student_id'))
    student_name=student_id.first_name+" "+student_id.last_name
    year=request.session['year']
    course_id = Courses.objects.get(id=request.session['class_id'])

    exam_type = request.session['exam_type']
    student_userid = student_id.username
    course = request.session['class']
    create_primary_key = year + course + student_userid + exam_type
    print(create_primary_key)
    id_exist = StudentsResult.objects.filter(id=create_primary_key).first()
    if id_exist != None:
       jsonDec = json.decoder.JSONDecoder()
       mypythonlist = jsonDec.decode(id_exist.myList)
       print('mypythonlist :', mypythonlist,len(mypythonlist))
       teacher_name=mypythonlist[7]
       course=mypythonlist[6]
       return render(request, "staff_template/edit_report.html")
    '''context = {
        "student_name": student_name,
        "year": year,
        "test": test,
        "student_id": student_id,
        "student": student,
        "teacher_name": teacher_name,
        "course": course,
        "subjects": subjects,

        }'''

    return HttpResponse(True)