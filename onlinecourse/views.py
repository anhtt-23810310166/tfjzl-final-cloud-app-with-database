from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
# IMPORT CÁC MODEL MỚI VÀO ĐÂY (Question, Choice, Submission)
from .models import Course, Enrollment, Question, Choice, Submission
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.

def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return redirect(f'/onlinecourse/{course.id}/')

# Hàm trích xuất danh sách ID đáp án từ form nộp bài
def extract_answers(request):
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            # Xử lý nếu value là một list (trong trường hợp checkbox chọn nhiều đáp án)
            if isinstance(value, list):
                for v in value:
                    submitted_answers.append(int(v))
            else:
                submitted_answers.append(int(value))
    return submitted_answers


# TRIỂN KHAI HÀM SUBMIT (TASK 5)
def submit(request, course_id):
    if not request.user.is_authenticated:
        return redirect('onlinecourse:login')

    course = get_object_or_404(Course, pk=course_id)

    if request.method == 'POST':
        # Lấy thông tin Enrollment của học viên đối với khóa học hiện tại
        enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
        
        # Tạo bản ghi Submission mới liên kết với Enrollment này
        submission = Submission.objects.create(enrollment=enrollment)
        
        # Gom toàn bộ choice_id người dùng đã click chọn thông qua hàm extract_answers có sẵn
        selected_choice_ids = extract_answers(request)
        
        # Thêm các đối tượng Choice tương ứng vào bảng quan hệ Many-to-Many của bản ghi Submission
        for choice_id in selected_choice_ids:
            try:
                choice = Choice.objects.get(pk=choice_id)
                submission.choices.add(choice)
            except Choice.DoesNotExist:
                continue
                
        submission.save()
        
        # Chuyển hướng dữ liệu sang view hiển thị kết quả kèm theo thông tin id bài nộp
        return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)
    
    return redirect(f'/onlinecourse/{course_id}/')


# TRIỂN KHAI HÀM SHOW_EXAM_RESULT (TASK 5)
def show_exam_result(request, course_id, submission_id):
    if not request.user.is_authenticated:
        return redirect('onlinecourse:login')

    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    # Lấy danh sách ID của tất cả các lựa chọn học viên đã làm để dùng làm bộ lọc so khớp dưới giao diện HTML
    selected_ids = [choice.id for choice in submission.choices.all()]
    
    context = {
        'course': course,
        'submission': submission,
        'selected_ids': selected_ids
    }
    
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
