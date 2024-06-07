from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group as AuthGroup


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not password:
            raise ValueError('The Password field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class Course(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    teachers = models.ManyToManyField('main_app.User', blank=True, limit_choices_to={'role': 'teacher'})

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'courses'


class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'modules'


class Group(AuthGroup):
    courses = models.ManyToManyField(Course, related_name='groups')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'groups'


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
        ('superadmin', 'SuperAdmin'),
    ]
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    degree = models.CharField(max_length=255, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(blank=True, null=True)
    groups = models.ManyToManyField(
        Group,
        related_name='main_app_user_group',
        blank=True,
        help_text=('The group this user belongs to. A user will get all permissions granted to their group.'),
        verbose_name=('group'),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='main_app_user_permissions',
        blank=True,
        help_text=('Specific permissions for this user.'),
        verbose_name=('user permissions'),
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'users'




class PracticalWork(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    course = models.ForeignKey(Course, models.CASCADE, blank=True, null=True)
    file = models.FileField(upload_to='practical_works/', blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    max_score = models.FloatField(default=10.0)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'practical_works'


class LectureMaterial(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    course = models.ForeignKey(Course, models.CASCADE, blank=True, null=True)
    file = models.FileField(upload_to='lecture_materials/', blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'lecture_materials'


class PracticalWorkSubmission(models.Model):
    id = models.AutoField(primary_key=True)
    practical_work = models.ForeignKey(PracticalWork, models.CASCADE, blank=True, null=True)
    student = models.ForeignKey(User, models.CASCADE, blank=True, null=True, limit_choices_to={'role': 'student'})
    file = models.FileField(upload_to='practical_work_submissions/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.IntegerField(blank=True, null=True)
    grade_date = models.DateTimeField(null=True, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE,
                                related_name='graded_practicals', null=True, blank=True)

    def __str__(self):
        return f"{self.student} - {self.practical_work}"

    class Meta:
        db_table = 'practical_work_submissions'
        unique_together = ('practical_work', 'student')


class Test(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    course = models.ForeignKey(Course, models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'tests'

class TestQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    test = models.ForeignKey(Test, models.CASCADE, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    is_multiple_choice = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.content

    class Meta:
        db_table = 'test_questions'

class QuestionOption(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(TestQuestion, models.CASCADE, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.content

    class Meta:
        db_table = 'question_options'

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    reviewer = models.ForeignKey(User, models.CASCADE, blank=True, null=True, related_name='reviewer')
    reviewee = models.ForeignKey(User, models.CASCADE, blank=True, null=True, related_name='reviewee')
    rating = models.IntegerField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.reviewer} reviews {self.reviewee}"

    class Meta:
        db_table = 'reviews'

class Schedule(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, models.CASCADE, blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.course} schedule"

    class Meta:
        db_table = 'schedule'

class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.CASCADE, blank=True, null=True)
    course = models.ForeignKey(Course, models.CASCADE, blank=True, null=True)
    login_time = models.DateTimeField(blank=True, null=True)
    logout_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} attendance in {self.course}"

    class Meta:
        db_table = 'attendance'

class Grade(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(User, models.CASCADE, blank=True, null=True, limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, models.CASCADE, blank=True, null=True)
    practical_work = models.ForeignKey(PracticalWork, models.CASCADE, blank=True, null=True)
    test = models.ForeignKey(Test, models.CASCADE, blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.student} grade in {self.course}"

    class Meta:
        db_table = 'grades'
