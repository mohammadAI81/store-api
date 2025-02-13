from django.dispatch import receiver
from store.signals import order_create


@receiver(order_create)
def after_order_creater(sender, **kwargs):
    print(f"create order {kwargs['order'].id}")