import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.text import slugify

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_uploader = models.BooleanField(
        default=False,
        verbose_name="Material Uploader",
        help_text="Can upload study materials"
    )
    
    # Department and Faculty relationships
    department = models.ForeignKey(
        'Department', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='users'
    )
    faculty = models.ForeignKey(
        'Faculty',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

class Faculty(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class Department(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, unique=True)
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name='departments'
    )
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class Category(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

class Level(models.Model):
    name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name

class Semester(models.Model):
    name = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.name

class Material(models.Model):
    title = models.CharField(max_length=50)
    code = models.CharField(
        max_length=10,
        blank=False,
        help_text="Course code (e.g. CSC101)"
    )
    file = models.FileField(upload_to='materials/')
    session = models.CharField(max_length=10)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, 
                null=True, blank=True, help_text="Select semester")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, 
                null=True, blank=True, help_text="Select material category")
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_materials'
    )
    upload_date = models.DateTimeField(auto_now_add=True)
    
    download_count = models.PositiveIntegerField(
        default=0, verbose_name='Download_count',
        help_text='Number of times this material has benn download'
    )

    def is_accessible_to(self, user):
        """Check if user can access this material"""
        return (user.is_superuser or 
                self.uploaded_by == user or 
                (user.is_uploader and user.department == self.department))

    def get_download_filename(self):
        """Generate download filename"""
        return f"{self.code}_{self.title}{os.path.splitext(self.file.name)[1]}"

    def __str__(self):
        return f"{self.code} ({self.title})"

    class Meta:
        ordering = ['-upload_date']
        verbose_name = "Material"
        verbose_name_plural = "Materials"
        permissions = [
            ('download_material', 'Can download material'),
        ]