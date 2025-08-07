from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator
from .models import CustomUser, Department, Faculty, Category, Level, Semester, Material

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'autofocus': True,
            'placeholder': 'Enter your email',
            'class': 'form-control'
        })
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': 'form-control'
        }),
    )

    error_messages = {
        'invalid_login': "Invalid email or password.",
        'inactive': "This account is inactive.",
    }

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address',
            'class': 'form-control'
        }),
        help_text="We'll never share your email with anyone else."
    )
    
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': 'Choose a username',
            'class': 'form-control'
        }),
        help_text="Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.",
        validators=[
            RegexValidator(
                r'^[\w.@+-]+$',
                'Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.'
            ),
        ]
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'First name (optional)',
            'class': 'form-control'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Last name (optional)',
            'class': 'form-control'
        })
    )
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
            'id': 'id_department'
        })
    )
    
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create a strong password',
            'class': 'form-control'
        }),
        help_text="Your password must contain at least 8 characters."
    )
    
    password2 = forms.CharField(
        label="Password Confirmation",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Repeat your password',
            'class': 'form-control'
        }),
        help_text="Enter the same password as before, for verification."
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'department', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'faculty' in self.data:
            try:
                faculty_id = int(self.data.get('faculty'))
                self.fields['department'].queryset = Department.objects.filter(faculty_id=faculty_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.faculty:
            self.fields['department'].queryset = self.instance.faculty.department_set.all()
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use. Please use a different email.")
        return email
        
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose a different one.")
        return username
        
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Your passwords don't match. Please try again.")
            
        return cleaned_data

class MaterialUploadForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=True,
        empty_label="Select Department",
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
            'id': 'id_department'
        })
    )
    
    
    class Meta:
        model = Material
        fields = ['department', 'level', 'title', 'code', 'category', 'semester', 'session', 'file']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Material title',
                'class': 'form-control'
            }),
            'code': forms.TextInput(attrs={
                'placeholder': 'e.g. CSC101',
                'class': 'form-control'
            }),
            'category' : forms.Select(attrs={'class': 'form-control'}),
            'level': forms.Select(attrs={'class': 'form-control'}),
            'semester': forms.Select(attrs={'class': 'form-control'}),
            'session': forms.TextInput(attrs={
            'placeholder': '2022/2023',
                'class': 'form-control'
            }),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and user.is_uploader:
            self.fields['department'].queryset = Department.objects.filter(id=user.department.id)
            self.fields['department'].initial = user.department
            self.fields['department'].disabled = True
            
            self.fields['category'].queryset = Category.objects.all()

            self.fields['semester'].queryset = Semester.objects.all()

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # File extension validation
            valid_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.zip']
            if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError(
                    'Unsupported file format. Please upload: PDF, Word, PowerPoint, or ZIP files.'
                )
            
            # File size validation (25MB max)
            max_size = 25 * 1024 * 1024
            if file.size > max_size:
                raise forms.ValidationError(
                    f'File size exceeds {max_size//(1024*1024)}MB limit. Your file: {file.size//(1024*1024)}MB'
                )
        return file

class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ['name', 'code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'faculty']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'faculty': forms.Select(attrs={'class': 'form-control'}),
        }