from celery import shared_task
from django.db import transaction
from django.utils import timezone


@shared_task
def assign_retreat_tomatoes():
    """
    Assign tomatoes to all active users of a retreat if one of the date passed.
    """
    from retirement.models import RetreatDate
    today = timezone.now()
    to_assign_dates = RetreatDate.objects.filter(
        end_time__lte=today,
        tomatoes_assigned=False,
    )

    for date in to_assign_dates:
        with transaction.atomic():
            active_reservations = date.retreat.reservations.filter(
                is_active=True)
            for reservation in active_reservations:
                from tomato.models import Tomato
                Tomato.objects.create(
                    user=reservation.user,
                    number_of_tomato=date.number_of_tomatoes,
                    source=Tomato.TOMATO_SOURCE_RETREAT,
                    content_object=reservation,
                )
            date.tomatoes_assigned = True
            date.save()
