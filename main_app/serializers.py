from rest_framework import serializers
from .models import User, Course, PracticalWork, Test, TestQuestion, QuestionOption, Review, Schedule, Attendance, Grade

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'bio', 'phone_number', 'degree', 'profile_photo', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'student'),
            bio=validated_data.get('bio', ''),
            phone_number=validated_data.get('phone_number', ''),
            degree=validated_data.get('degree', ''),
            profile_photo=validated_data.get('profile_photo', ''),
        )
        return user

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'



class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = '__all__'
