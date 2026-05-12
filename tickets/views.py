from django.db import transaction
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from tickets.models import Ticket, TicketEvent
from tickets.serializers import TicketResponseSerializer, TicketCreateSerializer


class TicketListCreateView(APIView):
    """
    GET  /api/tickets/  — список талонов
    POST /api/tickets/  — создание талона
    """

    @extend_schema(
        summary="Получить список талонов",
        description="Возвращает список всех талонов в системе.",
        responses={
            200: TicketResponseSerializer(many=True),
        },
        tags=["Tickets"],
    )
    def get(self, request):
        tickets = (
            Ticket.objects
            .select_related("ticket_type", "current_operator")
            .all()
        )

        serializer = TicketResponseSerializer(tickets, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Создать новый талон",
        description=(
            "Создаёт новый талон выбранного типа. "
            "Номер талона генерируется автоматически внутри выбранного типа."
        ),
        request=TicketCreateSerializer,
        responses={
            201: TicketResponseSerializer,
            400: OpenApiResponse(description="Ошибка валидации входных данных"),
        },
        examples=[
            OpenApiExample(
                name="Создание талона типа A",
                value={
                    "ticket_type": 1
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Успешный ответ",
                value={
                    "id": 1,
                    "ticket_type": 1,
                    "ticket_type_code": "A",
                    "ticket_type_name": "Консультация",
                    "number": 1,
                    "ticket_code": "A-1",
                    "status": "waiting",
                    "current_operator": None,
                    "created_at": "2026-05-10T12:30:00Z",
                    "called_at": None,
                    "started_at": None,
                    "finished_at": None,
                },
                response_only=True,
                status_codes=["201"],
            ),
        ],
        tags=["Tickets"],
    )
    @transaction.atomic
    def post(self, request):
        input_serializer = TicketCreateSerializer(data=request.data)

        if not input_serializer.is_valid():
            return Response(
                input_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        ticket_type = input_serializer.validated_data["ticket_type"]

        last_ticket = (
            Ticket.objects
            .select_for_update()
            .filter(ticket_type=ticket_type)
            .order_by("-number")
            .first()
        )

        next_number = last_ticket.number + 1 if last_ticket else 1

        ticket = Ticket.objects.create(
            ticket_type=ticket_type,
            number=next_number,
            status=Ticket.Status.WAITING,
        )

        TicketEvent.objects.create(
            ticket=ticket,
            event_type=TicketEvent.EventType.CREATED,
            comment="Талон создан"
        )

        output_serializer = TicketResponseSerializer(ticket)

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED
        )
