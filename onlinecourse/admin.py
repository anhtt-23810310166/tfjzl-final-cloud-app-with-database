from django.contrib import admin
# Đã import đủ các model cũ và các model mới được thêm vào (Question, Choice, Submission)
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission

# 1. Cấu hình ChoiceInline để hiển thị các lựa chọn ngay trong giao diện của Question
class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 4

# 2. Cấu hình QuestionInline để hiển thị các câu hỏi ngay trong giao diện của Course
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2

# 3. Cấu hình QuestionAdmin kết hợp với ChoiceInline
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ['question_text', 'course', 'grade']

# 4. Cấu hình LessonAdmin hiển thị danh sách tiêu đề bài học
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title']

# Cấu hình LessonInline để nhúng vào CourseAdmin
class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 5

# Cấu hình CourseAdmin kết hợp cả LessonInline và QuestionInline mới
class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline, QuestionInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']


# Đăng ký các Model và Class Admin vào hệ thống Django Admin
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission)
