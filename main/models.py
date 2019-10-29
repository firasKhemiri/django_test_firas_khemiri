from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.urls import reverse_lazy


class User(AbstractUser):
    AbstractUser._meta.get_field('email')._unique = True

    def get_all_orders(self):
        try:
            if self.user_order.count() > 0:
                orders = self.user_order.order_by('-id').all()
                return [{'id': order.id, 'object': order.object, 'price': order.price} for order in orders]

        except IndexError:
            return None


class Order(models.Model):
    object = models.CharField(max_length=255, blank=False, unique=False)

    price = models.FloatField(blank=False)

    image = models.TextField(blank=True)

    user = models.ForeignKey(User,
                             related_name='user_order',
                             on_delete=models.CASCADE)

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}".format(self.object)

    def get_absolute_url(self):
        return reverse_lazy('order_view', kwargs={'order_id': self.id})

    def get_orders_with_similar_price(self):
        try:
            orders = Order.objects.filter(Q(price=self.price) & ~Q(id=self.id)).order_by('-id').all()
            return [{'id': order.id, 'object': order.object, 'price': order.price} for order in orders]

        except IndexError:
            return None
