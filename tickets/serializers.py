from rest_framework import serializers
from .models import Ticket, TicketType, TicketEvent, OperatorTicketType


class TicketCreateSerializer(serializers.Serializer):
    """
    Serializer для входных данных при создании талона.
    """

    ticket_type = serializers.PrimaryKeyRelatedField(
        queryset=TicketType.objects.filter(is_active=True),
        help_text="ID активного типа талона"
    )


class TicketResponseSerializer(serializers.ModelSerializer):
    """
    Serializer для выходных данных талона.
    """

    ticket_code = serializers.SerializerMethodField()
    ticket_type_code = serializers.CharField(
        source="ticket_type.code",
        read_only=True
    )
    ticket_type_name = serializers.CharField(
        source="ticket_type.name",
        read_only=True
    )

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_type",
            "ticket_type_code",
            "ticket_type_name",
            "number",
            "ticket_code",
            "status",
            "current_operator",
            "created_at",
            "called_at",
            "started_at",
            "finished_at",
        ]

    def get_ticket_code(self, obj):
        return f"{obj.ticket_type.code}-{obj.number}"
