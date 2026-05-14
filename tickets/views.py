from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from tickets.models import Ticket, TicketEvent, TicketType
from tickets.serializers import VisitorTicketResponseSerializer, VisitorTicketCreateSerializer, \
    VisitorTicketTypeSerializer


class VisitorTicketTypeListView(APIView):
    """
    GET /api/visitor/ticket-types/
    Возвращает активные типы талонов для кнопок посетителя.
    """

    @extend_schema(
        summary="Получить кнопки для посетительского окна",
        description="Возвращает активные типы талонов, из которых формируются кнопки.",
        responses={200: VisitorTicketTypeSerializer(many=True)},
        tags=["Visitor"],
    )
    def get(self, request):
        ticket_types = (
            TicketType.objects
            .filter(is_active=True)
            .order_by("code")
        )

        serializer = VisitorTicketTypeSerializer(ticket_types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VisitorTicketCreateView(APIView):
    """
    POST /api/visitor/tickets/
    Создаёт талон выбранного типа для посетителя.
    """

    @extend_schema(
        summary="Создать талон для посетителя",
        description=(
            "Создаёт талон выбранного активного типа. "
            "Номер генерируется внутри типа талона и текущей даты обслуживания."
        ),
        request=VisitorTicketCreateSerializer,
        responses={
            201: VisitorTicketResponseSerializer,
            400: OpenApiResponse(description="Ошибка валидации входных данных"),
        },
        examples=[
            OpenApiExample(
                name="Создание талона",
                value={"ticket_type": 1},
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
                    "service_date": "2026-05-14",
                    "created_at": "2026-05-14T09:00:00Z",
                },
                response_only=True,
                status_codes=["201"],
            ),
        ],
        tags=["Visitor"],
    )
    @transaction.atomic
    def post(self, request):
        serializer = VisitorTicketCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        ticket_type = serializer.validated_data["ticket_type"]
        service_date = timezone.localdate()

        # Важно: номер ищем не просто по типу талона,
        # а по типу талона + текущей дате обслуживания.
        last_ticket = (
            Ticket.objects
            .select_for_update()
            .filter(
                ticket_type=ticket_type,
                service_date=service_date,
            )
            .order_by("-number")
            .first()
        )

        next_number = last_ticket.number + 1 if last_ticket else 1

        ticket = Ticket.objects.create(
            ticket_type=ticket_type,
            service_date=service_date,
            number=next_number,
            status=Ticket.Status.WAITING,
        )

        TicketEvent.objects.create(
            ticket=ticket,
            event_type=TicketEvent.EventType.CREATED,
            comment="Талон создан посетителем"
        )

        # Позже здесь будет вызов автобалансировщика:
        # assign_ticket_to_available_operator(ticket)

        output_serializer = VisitorTicketResponseSerializer(ticket)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class TicketListCreateView(APIView):
    """
    GET  /api/tickets/  — список талонов
    POST /api/tickets/  — создание талона
    """

    @extend_schema(
        summary="Получить список талонов",
        description="Возвращает список всех талонов в системе.",
        responses={
            200: VisitorTicketResponseSerializer(many=True),
        },
        tags=["Tickets"],
    )
    def get(self, request):
        tickets = (
            Ticket.objects
            .select_related("ticket_type", "current_operator")
            .all()
        )

        serializer = VisitorTicketResponseSerializer(tickets, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Создать новый талон",
        description=(
            "Создаёт новый талон выбранного типа. "
            "Номер талона генерируется автоматически внутри выбранного типа."
        ),
        request=VisitorTicketCreateSerializer,
        responses={
            201: VisitorTicketResponseSerializer,
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
        input_serializer = VisitorTicketCreateSerializer(data=request.data)

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
