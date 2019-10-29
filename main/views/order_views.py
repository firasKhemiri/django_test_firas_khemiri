from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from main.forms import OrderForm
from main.helpers import encode_to_base64
from main.models import User, Order


@csrf_exempt  # Disables Django's CSRF validation.
def get_order_picture(request, order_id):
    if request.method == 'GET':

        # Get Order object by id and return its image.
        if order_id is not None:
            try:
                order = Order.objects.get(pk=order_id)
                data = {'image': order.image}
                return JsonResponse(data)

            except Order.DoesNotExist:
                return JsonResponse("Order doesn't exist", safe=False)
        else:
            return JsonResponse("Order id not provided", safe=False)
    else:
        return JsonResponse("Method " + request.method + " not allowed", safe=False)


class OrderCRUDView(View):  # pylint: disable=too-few-public-methods
    @method_decorator(csrf_exempt)  # Disables Django's CSRF validation.
    def dispatch(self, request, *args, **kwargs):
        return super(OrderCRUDView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request, order_id):  # pylint: disable=unused-argument,invalid-name,redefined-builtin
        if order_id is not None:
            try:
                order = Order.objects.get(pk=order_id)

                order_user_data = {'id': order.user.id, 'username': order.user.username}
                data = {'id': order.id, 'object': order.object, 'price': order.price, 'user': order_user_data,
                        "orders with the same price": order.get_orders_with_similar_price()}

                return JsonResponse(data)

            except Order.DoesNotExist:
                return JsonResponse("Object doesn't exist", safe=False)

        else:
            order_list = Order.objects.all().order_by('-id').all()
            data = [{'id': order.id, 'object': order.object, 'price': order.price,
                     'user': {'id': order.user.id, 'username': order.user.username}} for order in order_list]

            return JsonResponse({'all orders': data})

    @staticmethod
    def post(request, *args, **kwargs):  # pylint: disable=unused-argument

        #  Check whether the data is valid or not.
        form = OrderForm(request.POST)
        if form.is_valid():
            #  Get order object attributes.
            order_object = request.POST.get('object', '')
            price = request.POST.get('price', '')
            user_id = request.POST.get('user', '')
            user = User.objects.get(id=user_id)

            # Get the uploaded image and encode it to base64.
            encoded_img = ''
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                encoded_img = encode_to_base64(image_file)

            #  Persist the object.
            order = Order.objects.create(object=order_object, price=price, image=encoded_img, user=user)

            #  Return order data as a Json response.
            order_user_data = {'id': order.user.id, 'username': order.user.username}
            data = {'id': order.id, 'object': order.object, 'price': order.price, 'user': order_user_data}
            return JsonResponse(data)

        else:
            # Returns the cause of the invalid found data.
            return JsonResponse(form.errors)

    @staticmethod
    def put(request, order_id):

        if order_id is not None:
            try:
                order = Order.objects.get(pk=order_id)
            except Order.DoesNotExist:
                return JsonResponse("Order doesn't exist", safe=False)

            #  If any of these parameters exist in the request, the corresponding attributes values
            #  of the found object will be replaced with them.
            if 'price' in request.PUT:
                order.price = request.PUT["price"]

            if 'object' in request.PUT:
                order.object = request.PUT["object"]

            if 'user' in request.PUT:
                #  Check if user exists and affect it the found Order instance.
                try:
                    user_id = request.PUT["user"]
                    user = User.objects.get(id=user_id)
                    order.user = user
                except User.DoesNotExist:
                    return JsonResponse("User doesn't exist", safe=False)

            order_form = OrderForm({'object': order.object, 'price': order.price, 'user': order.user.id},
                                   instance=order)

            #  Check if the data in the updated instance is valid,
            #  if it's valid, update the object in the database.
            if order_form.is_valid():
                if 'image' in request.FILES:
                    image_file = request.FILES['image']
                    encoded_img = encode_to_base64(image_file)
                    order.image = encoded_img

                order.save()

                #  Return the updated object in JSON format.
                order_user_data = {'id': order.user.id, 'username': order.user.username}
                data = {'id': order.id, 'object': order.object, 'price': order.price, 'user': order_user_data}
                return JsonResponse(data)
            else:
                return JsonResponse(order_form.errors)
        else:
            return JsonResponse("Order id not provided", safe=False)

    @staticmethod
    def delete(request, order_id):  # pylint: disable=unused-argument,invalid-name,redefined-builtin
        if order_id is not None:
            try:
                order = Order.objects.get(pk=order_id)
                order.delete()
                return JsonResponse("Order object deleted", safe=False)

            except Order.DoesNotExist:
                return JsonResponse("Order doesn't exist", safe=False)
        else:
            return JsonResponse("Order id not provided", safe=False)
