from django.db import models
from django.db.models.fields import IntegerField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    Кастомная модель пользователя.
    Добавляем related_name, чтобы избежать конфликтов со стандартной моделью User.
    """
    # Указываем уникальные имена для обратных связей
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set', # Новое имя
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set', # Новое имя
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.'
    )


class Address(models.Model):
    country = models.CharField(max_length=100, default="Россия", verbose_name="Страна")
    region = models.CharField(max_length=100, verbose_name="Регион (Край/Область)")
    district = models.CharField(max_length=100, blank=True, verbose_name="Район")
    city = models.CharField(max_length=100, verbose_name="Город/Село")
    street = models.CharField(max_length=150, verbose_name="Улица")
    building_number = models.CharField(max_length=10, verbose_name="Номер дома/строения")
    postal_code = models.CharField(max_length=10, verbose_name="Почтовый индекс", blank=True)
    description = models.TextField(blank=True, verbose_name="Примечание к адресу")

    def __str__(self):
        # Формируем красивый адрес
        address_parts = [
            self.country,
            self.region,
            self.city,
            self.street,
            self.building_number
        ]
        return ", ".join(filter(None, address_parts))

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"


class School(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название школы")
    addresses = models.ManyToManyField(Address, blank=True, verbose_name="Адреса школы")
    description = models.TextField(blank=True, verbose_name="Описание школы")
    photo = models.ImageField(
        upload_to='school_photos/',
        blank=True,
        null=True,
        verbose_name="Логотип или фото школы"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Школа"
        verbose_name_plural = "Школы"
        ordering = ['name']


class SchoolClass(models.Model):
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        verbose_name="Учебное заведение"
    )

    start_year = models.IntegerField(
        verbose_name="Год начала обучения",
        validators=[MinValueValidator(1900)]
    )

    end_year = models.IntegerField(
        verbose_name="Год окончания обучения",
        editable=False
    )

    grade_number = models.IntegerField(
        verbose_name="Номер класса",
        validators=[MinValueValidator(1), MaxValueValidator(12)]  # Ограничим от 1 до 12
    )

    letter = models.CharField(max_length=1,
                              verbose_name="Буква класса",
                              blank=True,
                              null=True)
    description = models.TextField(blank=True, verbose_name="Описание класса")
    photo = models.ImageField(
        upload_to='class_photos/',
        blank=True,
        null=True,
        verbose_name="Фото класса"
    )

    def __str__(self):
        grade_str = str(self.grade_number)
        if self.letter:
            grade_str += f" {self.letter}"

        return f"{grade_str} ({self.start_year}-{self.end_year}) ({self.school.name})"

    def save(self, *args, **kwargs):
        self.end_year = self.start_year + 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Класс"
        verbose_name_plural = "Классы"
        ordering = ['start_year', 'grade_number', 'letter']


class StudentClassHistory(models.Model):
    student = models.ForeignKey(
        'Student',
        on_delete=models.CASCADE,
        verbose_name="Ученик",
        related_name='classes_history')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, verbose_name="Класс")
    date_from = models.DateField(verbose_name="Дата поступления")
    date_to = models.DateField(verbose_name="Дата окончания", null=True, blank=True)

    def __str__(self):
        return f"{self.student} учился в {self.school_class} с {self.date_from} по {self.date_to or 'настоящее время'}"

    class Meta:
        verbose_name = "История обучения"
        verbose_name_plural = "Истории обучения"
        ordering = ['-date_from']


class Student(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    description = models.TextField(blank=True, verbose_name="О себе или примечания")
    photo = models.ImageField(
        upload_to='student_photos/',
        blank=True,
        null=True,
        verbose_name="Фотография ученика"
    )


    user = models.OneToOneField(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Связанный пользователь",
        help_text="Учетная запись, которой принадлежит этот ученик."
    )

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    class Meta:
        verbose_name = "Ученик"
        verbose_name_plural = "Ученики"
        ordering = ['last_name', 'first_name']

    # Удобный метод для получения текущего класса
    def get_current_class(self):
        current_history = self.classes_history.filter(date_to__isnull=True).first()
        return current_history.school_class if current_history else None


class Position(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название должности")
    description = models.TextField(blank=True, verbose_name="Описание должности")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"


class Employee(models.Model):
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        verbose_name="Место работы"
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Занимаемая должность"
    )
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    hire_year = models.IntegerField(verbose_name="Год приема на работу")
    description = models.TextField(blank=True, verbose_name="О сотруднике")

    photo = models.ImageField(
        upload_to='employee_photos/',
        blank=True,
        null=True,
        verbose_name="Фотография сотрудника"
    )

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.position})"

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"


class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название предмета")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"


class Teacher(Employee):
    subjects = models.ManyToManyField(
        Subject,
        blank=True,
        verbose_name="Преподаваемые предметы"
    )
    classes_teaches = models.ManyToManyField(
        SchoolClass,
        related_name='teachers',
        blank=True,
        verbose_name="Классы (преподавание)"
    )

    class Meta:
        # Указываем понятные названия для наследуемой модели
        verbose_name = "Учитель"
        verbose_name_plural = "Учителя"