from rest_framework import serializers
from .models import Ticket, TicketType, TicketEvent, OperatorTicketType


class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = "__all__"


class TicketSerializer(serializers.ModelSerializer):
    ticket_code = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_type",
            "number",
            "ticket_code",
            "status",
            "current_operator",
            "created_at",
            "called_at",
            "started_at",
            "finished_at",
        ]
        read_only_fields = [
            "number",
            "status",
            "current_operator",
            "created_at",
            "called_at",
            "started_at",
            "finished_at",
        ]

    def get_ticket_code(self, obj):
        return f"{obj.ticket_type.code}-{obj.number}"


class TicketEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketEvent
        fields = "__all__"