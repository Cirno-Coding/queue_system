from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from tickets.models import Ticket
from tickets.serializers import TicketSerializer


class TicketListView(APIView):
    def get(self, request):
        tickets = Ticket.objects.all()
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)


class TicketCreateView(APIView):
    def post(self, request):
        serializer = TicketSerializer(data=request.data)

        if serializer.is_valid():
            ticket_type = serializer.validated_data["ticket_type"]

            last_ticket = (
                Ticket.objects
                .filter(ticket_type=ticket_type)
                .order_by("-number")
                .first()
            )

            next_number = last_ticket.number + 1 if last_ticket else 1

            ticket = Ticket.objects.create(
                ticket_type=ticket_type,
                number=next_number,
                status=Ticket.Status.WAITING
            )

            response_serializer = TicketSerializer(ticket)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
