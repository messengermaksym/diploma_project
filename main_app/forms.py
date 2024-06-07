from django import forms
from .models import User, PracticalWorkSubmission, Course, Module, Group, LectureMaterial, PracticalWork


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_photo', 'first_name', 'last_name', 'bio', 'phone_number']


class PracticalWorkSubmissionForm(forms.ModelForm):
    class Meta:
        model = PracticalWorkSubmission
        fields = ['file']


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'content']


ModuleFormSet = forms.inlineformset_factory(Course, Module, form=ModuleForm, extra=1, can_delete=True)


class LectureMaterialForm(forms.ModelForm):
    class Meta:
        model = LectureMaterial
        fields = ['title', 'file']


LectureMaterialFormSet = forms.inlineformset_factory(Course, LectureMaterial, form=LectureMaterialForm, extra=1,
                                                     can_delete=True)


class PracticalWorkForm(forms.ModelForm):
    class Meta:
        model = PracticalWork
        fields = ['title', 'file']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


PracticalWorkFormSet = forms.inlineformset_factory(Course, PracticalWork, form=PracticalWorkForm, extra=1,
                                                   can_delete=True)


class CourseForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False)

    class Meta:
        model = Course
        fields = ['title', 'description', 'teachers', 'groups']

    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['groups'].initial = self.instance.groups.all()

    def save(self, commit=True):
        instance = super(CourseForm, self).save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
        instance.groups.set(self.cleaned_data['groups'])
        return instance
