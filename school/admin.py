from django.contrib import admin
from .models import School, SchoolClass, Student, Position, Employee, Subject, Teacher, Address, StudentClassHistory
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

class PhotoAdminMixin:
    """Миксин для отображения фото в списке моделей."""
    def photo_tag(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width:60px; height:auto; border-radius: 5px;" />',
                obj.photo.url
            )
        return "Нет фото"
    photo_tag.short_description = 'Превью'

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('city', 'street', 'building_number', 'postal_code')
    search_fields = ('city', 'street')

@admin.register(School)
class SchoolAdmin(PhotoAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'photo_tag', 'description')
    search_fields = ('name',)
    filter_horizontal = ('addresses',)

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'school', 'start_year', 'letter')
    list_filter = ('school', 'start_year')
    search_fields = ('letter', 'start_year')


class GradeNumberListFilter(admin.SimpleListFilter):
    # Текст для заголовка фильтра
    title = _('Номер класса')

    # Параметр для URL, который будет использоваться для фильтрации
    parameter_name = 'grade_number'

    def lookups(self, request, model_admin):
        """
        Возвращает список кортежей (value, label).
        value — это то, что пойдет в URL.
        label — то, что увидит пользователь.
        """
        # Получаем уникальные номера классов из базы данных
        grades = SchoolClass.objects.values_list('grade_number', flat=True).distinct().order_by('grade_number')
        return [(str(grade), f"{grade} класс") for grade in grades]

    def queryset(self, request, queryset):
        """
        Возвращает отфильтрованный queryset.
        """
        if self.value():
            # Если пользователь выбрал фильтр (например, '10'),
            # мы ищем учеников, у которых в истории есть класс с этим номером.
            return queryset.filter(classes_history__school_class__grade_number=self.value())


class StudentClassHistoryInline(admin.TabularInline):
    """
    Этот класс позволяет редактировать историю обучения
    прямо на странице редактирования ученика.
    """
    model = StudentClassHistory
    extra = 1 # Показываем одну пустую форму для быстрого добавления
    fields = ('school_class', 'date_from', 'date_to')
    verbose_name = "Запись об обучении"
    verbose_name_plural = "История обучения"


@admin.register(Student)
class StudentAdmin(PhotoAdminMixin, admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'get_current_class_display', 'photo_tag')
    list_filter = (
        GradeNumberListFilter,
        'classes_history__school__name',
    )

    search_fields = ('last_name', 'first_name')
    inlines = [StudentClassHistoryInline]

    def get_current_class_display(self, obj):
        current_class = obj.get_current_class()
        if current_class:
            return str(current_class)
        return "Нет класса"

    get_current_class_display.short_description = 'Текущий класс'

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Employee)
class EmployeeAdmin(PhotoAdminMixin, admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'position', 'hire_year', 'photo_tag')
    list_filter = ('position', 'hire_year')
    search_fields = ('last_name',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name')
    filter_horizontal = ('subjects', 'classes_teaches')
    search_fields = ('last_name', 'subjects__name')
