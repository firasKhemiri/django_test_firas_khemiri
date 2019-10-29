from django.conf.urls import url

from main.views.order_views import OrderCRUDView, get_order_picture
from main.views.user_views import signup, UserCRUDView

urlpatterns = [

    #  Only possible method is POST.
    url(r'^signup/?$', signup, name='signup'),

    #  url works with or without '/' at the end.
    #  Possible methods: GET, PUT, DELETE.
    url(r'^users(/?|(?:/(?P<user_id>\d+)/?)?)$', UserCRUDView.as_view(), name="user"),

    #  url works with or without '/' at the end.
    #  Possible methods: POST, GET, PUT, DELETE.
    url(r'^orders(/?|(?:/(?P<order_id>\d+)/?)?)$', OrderCRUDView.as_view(), name="order"),

    #  Only possible method is GET.
    url(r'^orders/(?P<order_id>\d+)/picture/?$', get_order_picture, name="order_picture"),

]
