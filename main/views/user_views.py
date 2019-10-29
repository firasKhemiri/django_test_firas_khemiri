from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from main.forms import SignUpForm
from main.models import User


@csrf_exempt  # Disables Django's CSRF validation.
def signup(request):
    if request.method == 'POST':

        #  Check whether the data is valid or not.
        form = SignUpForm(request.POST)
        if form.is_valid():

            username = request.POST.get('username', '')
            email = request.POST.get('email', '')
            password = request.POST.get('password', '')
            is_admin = request.POST.get('is_admin', '')

            #  Create the user in the database.
            user = User.objects.create_user(username=username, email=email, password=password,
                                            is_staff=is_admin, is_superuser=is_admin)

            #  Get the user's data.
            data = {'id': user.id, 'username': user.username, 'email': user.email, 'admin': user.is_superuser}
            return JsonResponse(data)

        #  Return invalid fields.
        else:
            return JsonResponse(form.errors)
    else:
        return JsonResponse("Method " + request.method + " not allowed", safe=False)


class UserCRUDView(View):
    @method_decorator(csrf_exempt)  # Disables Django's CSRF validation.
    def dispatch(self, request, *args, **kwargs):
        return super(UserCRUDView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):
        return JsonResponse("Method " + request.method + " not allowed", safe=False)

    @staticmethod
    def get(request, user_id):

        # If user id is provided, get that specific user's data.
        if user_id is not None:
            try:
                user = User.objects.get(pk=user_id)
                data = {'username': user.username, 'email': user.email, 'admin': user.is_superuser,
                        'orders': user.get_all_orders()}
                return JsonResponse(data)

            except User.DoesNotExist:
                return JsonResponse("User doesn't exist", safe=False)

        #  If user id is not provided, get all users data.
        else:
            #  Checks whether the url contains the parameter admin, if it does, the function
            #  will get users filtered by the admin parameter, if not, it will get all users in the database.
            if 'admin' in request.GET:
                is_admin = request.GET['admin']
                queryset = User.objects.filter(is_superuser=is_admin)
            else:
                queryset = User.objects.all()

            count = queryset.count()
            users_list = [{'id': user.id, 'username': user.username, 'email': user.email, 'admin': user.is_superuser}
                          for user in queryset]

            data = ({'count': count, 'users': users_list})

            return JsonResponse(data)

    @staticmethod
    def put(request, user_id):
        if user_id is not None:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return JsonResponse("User doesn't exist", safe=False)

            #  If any of these parameters exist in the request object, the corresponding attributes values
            #  of the found user will be replaced with them.
            if 'username' in request.PUT:
                user.username = request.PUT["username"]

            if 'email' in request.PUT:
                user.email = request.PUT["email"]

            #  Check whether password parameter exist in the request,
            #  if it does, check if it's valid and encrypt it when affecting to the user.
            if 'password' in request.PUT:
                password = request.PUT["password"]
                if len(password) > 7:
                    user.set_password(request.PUT["password"])
                else:
                    return JsonResponse("Invalid password", safe=False)

            if 'is_admin' in request.PUT:
                is_admin = request.PUT["is_admin"]
                user.is_superuser = is_admin

                print(user.is_superuser)
                user.is_staff = is_admin

            #  Check if the data in the user instance is valid,
            #  if it's valid, update the user in the database.
            user_form = SignUpForm({'username': user.username, 'email': user.email, 'password': user.password,
                                    'is_superuser': user.is_superuser}, instance=user)
            if user_form.is_valid():
                user.save()
                data = {'username': user.username, 'email': user.email, 'is_admin': user.is_superuser,
                        'password': user.password}
                return JsonResponse(data)
            else:
                return JsonResponse(user_form.errors)
        else:
            return JsonResponse("User id not provided", safe=False)

    @staticmethod
    def delete(request, user_id):
        if user_id is not None:
            try:
                user = User.objects.get(pk=user_id)
                user.delete()
                return JsonResponse("User " + user.username + " deleted", safe=False)

            except User.DoesNotExist:
                return JsonResponse("User doesn't exist", safe=False)
        else:
            return JsonResponse("User id not provided", safe=False)
