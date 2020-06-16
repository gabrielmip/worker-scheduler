from django.contrib import admin
from workforce.models import Calendar, Worker, Availability, WorkEvent, User


class WorkerAdmin(admin.ModelAdmin):
    def add_view(self, request, form_url='', extra_context=None):
        self.exclude = ('calendar',)
        return super().add_view(request, form_url=form_url, extra_context=extra_context)


admin.site.register(Calendar)
admin.site.register(Availability)
admin.site.register(Worker, WorkerAdmin)
admin.site.register(WorkEvent)
admin.site.register(User)
