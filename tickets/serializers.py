from rest_framework import serializers
from .models import Ticket, TicketType


class VisitorTicketTypeSerializer(serializers.ModelSerializer):
    """
    Сериализатор кнопок для окна посетителя.
    Каждая активная запись TicketType превращается в кнопку на экране.
    """

    class Meta:
        model = TicketType
        fields = [
            "id",
            "code",
            "name",
            "description",
        ]


class VisitorTicketCreateSerializer(serializers.Serializer):
    """
    Входные данные при создании талона посетителем.
    Посетитель выбирает только тип талона.
    """

    ticket_type = serializers.PrimaryKeyRelatedField(
        queryset=TicketType.objects.filter(is_active=True),
        help_text="ID активного типа талона"
    )


class VisitorTicketResponseSerializer(serializers.ModelSerializer):
    """
    Ответ для посетителя после создания талона.
    Именно эти данные можно показать на экране вместо печати.
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
            "service_date",
            "created_at",
        ]

    def get_ticket_code(self, obj):
        return f"{obj.ticket_type.code}-{obj.number}"

