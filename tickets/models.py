from django.contrib.auth.models import User
from django.db import models


class TicketType(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)


class OperatorTicketType(models.Model):
    operator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ticket_types"
    )

    ticket_type = models.ForeignKey(
        TicketType,
        on_delete=models.CASCADE,
        related_name="operators"
    )

    class Meta:
        unique_together = ("operator", "ticket_type")


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
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_tickets"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    called_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]


class TicketEvent(models.Model):
    class EventType(models.TextChoices):
        CREATED = "created", "Создан"
        CALLED = "called", "Вызван"
        STARTED = "started", "Начато обслуживание"
        COMPLETED = "completed", "Обслужен"
        NO_SHOW = "no_show", "Не явился"
        CANCELLED = "cancelled", "Отменён"
        RETURNED = "returned", "Возвращён в очередь"

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="events"
    )

    operator = models.ForeignKey(
        User,
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
