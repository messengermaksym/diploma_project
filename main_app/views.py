from django.utils import timezone
from django.db.models import Avg, Count
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import User, Course, Test, Group, PracticalWork, PracticalWorkSubmission, Grade
from .serializers import UserSerializer, CourseSerializer, TestSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib import messages
from django.conf import settings
from rest_framework import serializers
from .forms import ProfileForm, PracticalWorkSubmissionForm, CourseForm, ModuleFormSet, PracticalWorkFormSet, \
    LectureMaterialFormSet
import matplotlib.pyplot as plt
import io
import urllib, base64

def home(request):
    courses = Course.objects.all()
    return render(request, 'home.html', {'courses': courses})


def course_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user_has_access = request.user.groups.filter(courses=course).exists()
    return render(request, 'course_detail.html', {'course': course, 'user_has_access': user_has_access})


@login_required
def submit_practical_work(request, work_id):
    practical_work = get_object_or_404(PracticalWork, pk=work_id)
    course = practical_work.course
    submission, created = PracticalWorkSubmission.objects.get_or_create(
        practical_work=practical_work,
        student=request.user,
    )

    if request.method == 'POST':
        form = PracticalWorkSubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            form.save()
            return redirect('course_detail', course_id=course.id)
    else:
        form = PracticalWorkSubmissionForm(instance=submission)

    return render(request, 'submit_practical_work.html', {
        'course': course,
        'practical_work': practical_work,
        'form': form,
        'submission': submission,
    })


@login_required
def courses(request):
    user = request.user
    user_groups = user.groups.all()

    if user.role == 'student':
        # Показати курси для студентів
        courses = Course.objects.filter(groups__in=user_groups).distinct()
    elif user.role == 'teacher':
        # Показати курси для викладачів
        courses = Course.objects.filter(teachers=user).distinct()
    else:
        courses = []

    return render(request, 'courses.html', {'courses': courses, 'user_groups': user_groups, 'user_role': user.role})


@login_required
def create_course(request):
    if request.user.role != 'teacher':
        return redirect('courses')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.save()
            form.save_m2m()
            return redirect('courses')
    else:
        form = CourseForm()
    return render(request, 'create_course.html', {'form': form})

@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        course_form = CourseForm(request.POST, instance=course)
        module_formset = ModuleFormSet(request.POST, instance=course)
        lecture_material_formset = LectureMaterialFormSet(request.POST, request.FILES, instance=course)
        practical_work_formset = PracticalWorkFormSet(request.POST, request.FILES, instance=course)
        if course_form.is_valid() and module_formset.is_valid() and lecture_material_formset.is_valid() and practical_work_formset.is_valid():
            course_form.save()
            module_formset.save()
            lecture_material_formset.save()
            practical_work_formset.save()
            if 'delete' in request.POST:
                course.delete()
                return redirect('courses')
            return redirect('course_detail', course_id=course.id)
    else:
        course_form = CourseForm(instance=course)
        module_formset = ModuleFormSet(instance=course)
        lecture_material_formset = LectureMaterialFormSet(instance=course)
        practical_work_formset = PracticalWorkFormSet(instance=course)
    return render(request, 'edit_course.html', {
        'course_form': course_form,
        'module_formset': module_formset,
        'lecture_material_formset': lecture_material_formset,
        'practical_work_formset': practical_work_formset,
        'course': course,
    })


@login_required
def check_practicals(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    practical_works = PracticalWork.objects.filter(course=course)

    return render(request, 'check_practicals.html', {
        'course': course,
        'practical_works': practical_works,

    })

@login_required
def check_practical_details(request, course_id, practical_id):
    course = get_object_or_404(Course, id=course_id)
    practical_work = get_object_or_404(PracticalWork, id=practical_id)
    submissions = PracticalWorkSubmission.objects.filter(practical_work=practical_work)

    if request.method == 'POST':
        for submission in submissions:
            grade = request.POST.get(f'grade_{submission.id}')
            if grade:
                submission.grade = grade
                submission.grade_date = timezone.now()
                submission.teacher = request.user
            else:
                submission.grade = None
                submission.grade_date = None
                submission.teacher = None
            submission.save()
        return redirect('check_practical_details', course_id=course_id, practical_id=practical_id)

    groups = course.groups.all()
    submissions_by_group = {}
    for group in groups:
        group_submissions = submissions.filter(student__groups=group)
        submissions_by_group[group.name] = group_submissions

    return render(request, 'check_practical_details.html', {
        'course': course,
        'practical_work': practical_work,
        'submissions_by_group': submissions_by_group,
    })


def tests(request):
    return render(request, 'tests.html')


class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserUpdateView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include "email" and "password".')
        return super().validate(attrs)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': 'This is a protected view.'}
        return Response(content)


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password')
    return render(request, 'login.html')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})


def custom_404(request, exception):
    return render(request, '404.html', {}, status=404)


def logout_view(request):
    logout(request)
    return redirect('login')


def generate_plot(data, title):
    plt.figure(figsize=(10, 6))
    for label, values in data.items():
        if values['value'] is not None:  # Додано перевірку на None
            plt.bar(label, values['value'], label=values['label'])
    plt.title(title)
    plt.ylabel('Середня оцінка')
    plt.legend()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    return mark_safe(f'<img src="data:image/png;base64,{uri}" />')


def analytics(request):
    courses = Course.objects.all()
    data = []
    plots = []

    for course in courses:
        submissions = PracticalWorkSubmission.objects.filter(practical_work__course=course)
        avg_grade = submissions.aggregate(Avg('grade'))['grade__avg']

        groups = course.groups.all()
        total_students = User.objects.filter(groups__in=groups).distinct().count()
        students_passed_all = User.objects.filter(
            groups__in=groups,
            practicalworksubmission__practical_work__course=course,
            practicalworksubmission__grade__isnull=False
        ).distinct().count()

        practicals = PracticalWork.objects.filter(course=course)
        practical_data = []
        practical_plot_data = {}
        for practical in practicals:
            avg_practical_grade = practical.practicalworksubmission_set.aggregate(Avg('grade'))['grade__avg']
            students_submitted = practical.practicalworksubmission_set.filter(grade__isnull=False).count()
            practical_data.append({
                'title': practical.title,
                'avg_grade': avg_practical_grade,
                'students_submitted': students_submitted
            })
            practical_plot_data[practical.title] = {'value': avg_practical_grade, 'label': practical.title}

        practical_plot = generate_plot(practical_plot_data, f'Практичні роботи курсу {course.title}')
        plots.append(practical_plot)

        group_data = []
        group_plot_data = {}
        for group in groups:
            avg_group_grade = submissions.filter(student__groups=group).aggregate(Avg('grade'))['grade__avg']
            group_data.append({
                'name': group.name,
                'avg_grade': avg_group_grade
            })
            group_plot_data[group.name] = {'value': avg_group_grade, 'label': group.name}

        group_plot = generate_plot(group_plot_data, f'Успішність по групам курсу {course.title}')
        plots.append(group_plot)

        data.append({
            'course': course,
            'avg_grade': avg_grade,
            'total_students': total_students,
            'students_passed_all': students_passed_all,
            'practicals': practical_data,
            'groups': group_data
        })

    return render(request, 'analytics.html', {'data': data, 'plots': plots})



