from django.contrib import admin
from .models import Calendar, Worker


class WorkerAdmin(admin.ModelAdmin):
    def add_view(self, request, form_url='', extra_context=None):
        self.exclude = ('calendar',)
        return super().add_view(request, form_url=form_url, extra_context=extra_context)


admin.site.register(Calendar)
admin.site.register(Worker, WorkerAdmin)
