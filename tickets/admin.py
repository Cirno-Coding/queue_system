from django.contrib import admin
from tickets.models import TicketType, OperatorTicketType, Ticket, TicketEvent


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "is_active", "created_at")
    search_fields = ("code", "name")


@admin.register(OperatorTicketType)
class OperatorTicketTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "operator", "ticket_type")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ticket_type",
        "number",
        "status",
        "current_operator",
        "created_at",
        "started_at",
        "finished_at"
    )
    list_filter = ("status", "ticket_type")
    search_fields = ("number", )


@admin.register(TicketEvent)
class TicketEventAdmin(admin.ModelAdmin):
    list_display = ("id", "ticket", "operator", "event_type", "created_at")
    list_filter = ("event_type",)
