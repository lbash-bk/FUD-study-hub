from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Department, Faculty, Category, Level, Semester, Material
from .forms import SignUpForm

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'department', 'is_staff', 'is_uploader')
    list_filter = ('is_uploader', 'is_staff', 'is_superuser', 'department')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'department__name')
    ordering = ('email',)
    
    add_form = SignUpForm

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_uploader', 
                      'groups', 'user_permissions'),
        }),
        ('Department Info', {'fields': ('department',)}),
        ('faculty Info', {'fields': ('faculty',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.is_uploader:
            return qs.filter(department=request.user.department)
        return qs.none()

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'slug')
    search_fields = ('name', 'code')
    
    def has_module_permission(self, request):
        return request.user.is_superuser

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'faculty', 'slug')
    list_filter = ('faculty',)
    search_fields = ('name', 'code', 'faculty__name')
    
    def has_module_permission(self, request):
        return request.user.is_superuser

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    
    def has_module_permission(self, request):
        return request.user.is_superuser

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    
    def has_module_permission(self, request):
        return request.user.is_superuser

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

    def has_module_permission(self, request):
        return request.user.is_superuser

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'department', 'category', 'level', 'semester', 'upload_date', 'uploaded_by')
    list_filter = ('department', 'category', 'level', 'semester', 'upload_date')
    search_fields = ('title', 'code', 'department__name')
    readonly_fields = ('uploaded_by', 'upload_date')
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
    
    def has_module_permission(self, request):
        return request.user.is_authenticated and (request.user.is_superuser or request.user.is_uploader)
    
    def has_view_permission(self, request, obj=None):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if obj:
            return obj.department == request.user.department
        return request.user.is_uploader
    
    def has_add_permission(self, request):
        return request.user.is_authenticated and (request.user.is_uploader or request.user.is_superuser)
    
    def has_change_permission(self, request, obj=None):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if obj:
            return obj.uploaded_by == request.user or obj.department == request.user.department
        return request.user.is_uploader
    
    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.is_uploader:
            return qs.filter(department=request.user.department)
        return qs.none()
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "department" and request.user.is_uploader:
            kwargs["queryset"] = Department.objects.filter(id=request.user.department.id)
        if db_field.name == "category" and request.user.is_uploader:
            kwargs["queryset"] = Category.objects.filter(department=request.user.department)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(CustomUser, CustomUserAdmin)