import django.dispatch

confirmed = django.dispatch.Signal(providing_args=["toconfirm_type", "object_id"])

