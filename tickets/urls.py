from django.urls import path

from tickets.views import VisitorTicketTypeListView, VisitorTicketCreateView, TicketListCreateView

urlpatterns = [
    # Публичный API для посетительского окна.
    path(
        "visitor/ticket-types/",
        VisitorTicketTypeListView.as_view(),
        name="visitor-ticket-type-list",
    ),
    path(
        "visitor/tickets/",
        VisitorTicketCreateView.as_view(),
        name="visitor-ticket-create",
    ),

    # Общий/служебный API. Позже его можно ограничить правами.
    path("tickets/", TicketListCreateView.as_view(), name="ticket-list-create"),
]