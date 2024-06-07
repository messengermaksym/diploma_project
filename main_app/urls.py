from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
from .views import CustomTokenObtainPairView, ProtectedView, login_view

router = DefaultRouter()
router.register(r'courses', views.CourseViewSet)
router.register(r'tests', views.TestViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('courses/', views.courses, name='courses'),
    path('course/create/', views.create_course, name='create_course'),
    path('course/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/check_practicals/', views.check_practicals, name='check_practicals'),
    path('course/<int:course_id>/check_practicals/<int:practical_id>/', views.check_practical_details,
         name='check_practical_details'),
    path('submit_practical_work/<int:work_id>/', views.submit_practical_work, name='submit_practical_work'),
    path('tests/', views.tests, name='tests'),
    path('profile/', views.profile_view, name='profile'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/update/<int:pk>/', views.UserUpdateView.as_view(), name='user-update'),
    path('register/', views.UserRegisterView.as_view(), name='user-register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('api/', include(router.urls)),
    path('analytics/', views.analytics, name='analytics'),
]
