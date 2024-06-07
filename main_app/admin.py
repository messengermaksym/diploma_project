from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin as BaseUserAdmin
from .models import Course, Module, Test, PracticalWork, Group, TestQuestion, QuestionOption, Review, Schedule, \
    Attendance, Grade, User, LectureMaterial, PracticalWorkSubmission


class GroupAdminCustom(GroupAdmin):
    filter_horizontal = ['permissions', 'courses']


class UserAdmin(BaseUserAdmin):
    filter_horizontal = ['groups', 'user_permissions']
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'role', 'bio', 'phone_number', 'degree', 'profile_photo')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'bio', 'phone_number', 'degree', 'profile_photo', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1


class CourseAdmin(admin.ModelAdmin):
    inlines = [ModuleInline]
    list_display = ('title',)
    search_fields = ('title', 'description')
    filter_horizontal = ('teachers',)


admin.site.register(Group, GroupAdminCustom)
admin.site.register(Module)
admin.site.register(Course, CourseAdmin)
admin.site.register(Test)
admin.site.register(PracticalWork)
admin.site.register(LectureMaterial)
admin.site.register(PracticalWorkSubmission)
admin.site.register(TestQuestion)
admin.site.register(QuestionOption)
admin.site.register(Review)
admin.site.register(Schedule)
admin.site.register(Attendance)
admin.site.register(Grade)
admin.site.register(User, UserAdmin)

