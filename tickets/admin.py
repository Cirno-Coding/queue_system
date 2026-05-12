from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from tickets.models import TicketType, OperatorTicketType, Ticket, TicketEvent, OperatorProfile


class OperatorProfileInline(admin.StackedInline):
    model = OperatorProfile
    can_delete = False
    extra = 0

    fields = ("window_number", "is_online", "last_seen_at")
    readonly_fields = ("last_seen_at",)


@admin.action(description="Сгенерировать новый пароль для выбранных операторов")
def generate_operator_passwords(modeladmin, request, queryset):
    for user in queryset:
        password = get_random_string(length=10)
        user.set_password(password)
        user.save(update_fields=["password"])

        # Пароль можно показать только один раз, потому что в БД хранится хеш.
        messages.warning(
            request,
            f"Новый пароль для {user.username}: {password}"
        )


admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (OperatorProfileInline,)
    actions = (generate_operator_passwords,)

    list_display = (
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "get_window_number",
        "get_is_online",
    )

    def get_window_number(self, obj):
        profile = getattr(obj, "operator_profile", None)
        return profile.window_number if profile else "-"

    get_window_number.short_description = "Окно"

    def get_is_online(self, obj):
        profile = getattr(obj, "operator_profile", None)
        return profile.is_online if profile else False

    get_is_online.boolean = True
    get_is_online.short_description = "В сети"


class OperatorTicketTypeInline(admin.TabularInline):
    model = OperatorTicketType
    extra = 1
    autocomplete_fields = ("ticket_type",)


@admin.register(OperatorProfile)
class OperatorProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "window_number",
        "is_online",
        "last_seen_at",
        "created_at",
    )
    list_filter = ("is_online",)
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "window_number",
    )
    inlines = (OperatorTicketTypeInline,)


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
    ordering = ("code",)


@admin.register(OperatorTicketType)
class OperatorTicketTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "operator", "ticket_type")
    list_filter = ("ticket_type",)
    search_fields = (
        "operator__user__username",
        "operator__window_number",
        "ticket_type__code",
        "ticket_type__name",
    )
    autocomplete_fields = ("operator", "ticket_type")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ticket_type",
        "number",
        "status",
        "current_operator",
        "called_window_number",
        "service_date",
        "created_at",
        "assigned_at",
        "called_at",
        "started_at",
        "finished_at",
    )
    list_filter = ("status", "ticket_type", "service_date")
    search_fields = (
        "number",
        "ticket_type__code",
        "current_operator__user__username",
        "called_window_number",
    )
    readonly_fields = (
        "created_at",
        "assigned_at",
        "called_at",
        "started_at",
        "finished_at",
    )
    autocomplete_fields = ("ticket_type", "current_operator")


@admin.register(TicketEvent)
class TicketEventAdmin(admin.ModelAdmin):
    list_display = ("id", "ticket", "operator", "event_type", "created_at")
    list_filter = ("event_type", "created_at")
    search_fields = (
        "ticket__number",
        "ticket__ticket_type__code",
        "operator__user__username",
        "comment",
    )
    readonly_fields = ("ticket", "operator", "event_type", "comment", "created_at")
    autocomplete_fields = ("ticket", "operator")
