from django.contrib.auth.models import User
from django.db import models


class TicketType(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} — {self.name}"


class OperatorProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="operator_profile"
    )
    window_number = models.PositiveIntegerField(unique=True)
    is_online = models.BooleanField(default=False)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class OperatorTicketType(models.Model):
    operator = models.ForeignKey(
        OperatorProfile,
        on_delete=models.CASCADE,
        related_name="ticket_types"
    )

    ticket_type = models.ForeignKey(
        TicketType,
        on_delete=models.CASCADE,
        related_name="operators"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["operator", "ticket_type"],
                name="unique_operator_ticket_type"
            )
        ]


class Ticket(models.Model):
    class Status(models.TextChoices):
        WAITING = "waiting", "В очереди"
        CALLED = "called", "Вызван"
        IN_SERVICE = "in_service", "Обслуживается"
        COMPLETED = "completed", "Обслужен"
        NO_SHOW = "no_show", "Не явился"
        CANCELLED = "cancelled", "Отменён"

    ticket_type = models.ForeignKey(
        TicketType,
        on_delete=models.PROTECT,
        related_name="tickets"
    )

    number = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.WAITING
    )

    current_operator = models.ForeignKey(
        OperatorProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_tickets"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    called_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    service_date = models.DateField()
    called_window_number = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["ticket_type", "service_date", "number"],
                name="unique_ticket_number_per_type_per_day"
            )
        ]

    def __str__(self):
        return f"{self.ticket_type.code}-{self.number}"


class TicketEvent(models.Model):
    class EventType(models.TextChoices):
        CREATED = "created", "Создан"
        CALLED = "called", "Вызван"
        STARTED = "started", "Начато обслуживание"
        COMPLETED = "completed", "Обслужен"
        NO_SHOW = "no_show", "Не явился"
        CANCELLED = "cancelled", "Отменён"

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="events"
    )

    operator = models.ForeignKey(
        OperatorProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ticket_events"
    )

    event_type = models.CharField(
        max_length=30,
        choices=EventType.choices
    )

    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
