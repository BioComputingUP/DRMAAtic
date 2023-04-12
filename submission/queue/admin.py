from django.contrib import admin

from submission.queue.models import Queue


@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_cpu', 'max_mem')
