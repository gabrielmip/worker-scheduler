from django.contrib import admin
from workforce.models import Calendar, Worker, Availability, WorkEvent, User


class WorkEventAdmin(admin.ModelAdmin):
    date_hierarchy = 'start'
    list_display = ('full_name', 'email_address',
                    'start', 'workers', 'calendar', 'canceled_at')
    search_fields = ('user__full_name', 'user__email_address')

    def full_name(self, event):
        return event.user.full_name

    def email_address(self, event):
        return event.user.email_address

    def workers(self, event):
        return ', '.join([
            worker.auth_user.first_name
            for worker in event.calendar.worker_set.all()
        ])


admin.site.register(Calendar)
admin.site.register(Availability)
admin.site.register(Worker)
admin.site.register(WorkEvent, WorkEventAdmin)
admin.site.register(User)
