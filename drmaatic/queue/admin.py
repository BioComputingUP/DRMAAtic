from django.contrib import admin

from drmaatic.queue.models import Queue


@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_cpu', 'max_mem')
