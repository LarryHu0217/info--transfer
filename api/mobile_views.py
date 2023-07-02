
import random
import re

from .models import UserInformation

from .views import handle_user_survey

from django.views.decorators.csrf import csrf_exempt
import datetime
import pytz

# !/usr/bin/python

from django.http import JsonResponse
from http import HTTPStatus

@csrf_exempt
def register(request):
    """register"""
    if request.method == "POST":
        response = request.POST
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        if not (UserInformation.objects.filter(email=email).exists() or (
                UserInformation.objects.filter(phone=phone).exists())):
            users = UserInformation.objects.create(
                first_name=response.get("first_name"),
                last_name=response.get("last_name"),
                email=response.get("email"),
                password=response.get("password"),
                phone=response.get("phone"),
                due_date=datetime.datetime.strptime(
                    str(response.get("due_date")), "%Y-%m-%d"
                ).date()
            )
            handle_user_survey(users, daily_test=True)
        else:
            return JsonResponse(data={"message": 'already register!'}, status=HTTPStatus.OK)
    else:
        return JsonResponse(data={"message": "Bad method type"}, status=HTTPStatus.METHOD_NOT_ALLOWED)

@csrf_exempt
def login(request):
    """log in"""
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = UserInformation.objects.get(email=email)
            if user.password != password:
                return JsonResponse(data={"message": "Password not correct"}, status=HTTPStatus.BAD_REQUEST)
            else:
                return JsonResponse(data={"message": "Login successfully"}, status=HTTPStatus.OK)
        except Exception:
            return JsonResponse(data={"message": "User does not exist"}, status=HTTPStatus.BAD_REQUEST)
    else:
        return JsonResponse(data={"message": "Bad method type"}, status=HTTPStatus.METHOD_NOT_ALLOWED)

# Minimum 8 characters.
# The alphabets must be between [a-z]
# At least one alphabet should be of Upper Case [A-Z]
# At least 1 number or digit between [0-9].
# At least 1 character from [ _ or @ or $ ].

def password_check(password):

    flag = 0
    while True:
        if (len(password) < 8):
            flag = -1
            break
        elif not re.search("[a-z]", password):
            flag = -1
            break
        elif not re.search("[A-Z]", password):
            flag = -1
            break
        elif not re.search("[0-9]", password):
            flag = -1
            break
        elif not re.search("[_@$]", password):
            flag = -1
            break
        elif re.search("\s", password):
            flag = -1
            break
        else:
            flag = 0
            break
    if flag == -1:
        print("Not a Valid Password")
        return False
    elif flag==0:
        print("Valid Password")
        return True

@csrf_exempt
def update_password(request):
    """change password"""
    if request.method == "POST":
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        if (password_check(new_password)) == False:
            return JsonResponse(data={"message": "password is too simple"}, status=HTTPStatus.OK)
        else:
            try:
                userInformation = UserInformation.objects.get(email=email)
                userInformation.password=new_password
                return JsonResponse(data={"message": "password changed successfully"}, status=HTTPStatus.OK)
            except Exception:
                return JsonResponse(data={"message": "User does not exist"}, status=HTTPStatus.BAD_REQUEST)
    else:
        return JsonResponse(data={"message": "Bad method type"}, status=HTTPStatus.METHOD_NOT_ALLOWED)

#  change  request to user
@csrf_exempt
def send_otp(user):
    # phone = request.POST.get('phone')
    # email = request.POST.get('email')
        try:
            # user = UserInformation.objects.get(phone=phone, email=email)
            key= random.randint(999, 999999)
            cur = datetime.datetime.now()
            now= datetime.datetime.strptime(str(pytz.utc.localize(cur))[:19],'%Y-%m-%d %H:%M:%S')
            maxtime=datetime.datetime.strptime(str(now+datetime.timedelta(minutes=30 ))[:19], '%Y-%m-%d %H:%M:%S')
            user.otp_token = key
            user.otp_due_date=maxtime
            print("user's key", user.otp_token)
            user.save()
            return JsonResponse(data={"message": "send one-time-password"}, status=HTTPStatus.OK)
        except Exception:
            return JsonResponse(data={"message": "User does not exist"}, status=HTTPStatus.BAD_REQUEST)


@csrf_exempt
def verify_otp_token(request):
    if request.method == "POST":
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        otp = request.POST.get('otp_token')
        newpassword=request.POST.get("newpassword")
        try:
            user = UserInformation.objects.get(email=email, phone=phone)
            now= datetime.datetime.strptime(str(datetime.datetime.now())[:19],'%Y-%m-%d %H:%M:%S')
            otp_datetime =user.otp_due_date
            otp_datetime=datetime.datetime.strptime(str(otp_datetime)[:19],
                                                    '%Y-%m-%d %H:%M:%S')
            if now > otp_datetime:
                return JsonResponse(data={"message": "time out"}, status=HTTPStatus.OK)
            else:
                if user.otp_token == otp:
                    if (password_check(newpassword)) == False:
                        return JsonResponse(data={"message": "password is too simple"}, status=HTTPStatus.OK)
                    else:
                            userInformation = UserInformation.objects.get(email=email)
                            userInformation.password = newpassword
                            return JsonResponse(data={"message": "password changed successfully"}, status=HTTPStatus.OK)
                elif user.otp_token != otp:
                    return JsonResponse(data={"message": "OTP Verification failed"}, status=HTTPStatus.OK)
        except Exception:
            return JsonResponse(data={"message": "User does not exist"}, status=HTTPStatus.BAD_REQUEST)
    else:
        return JsonResponse(data={"message": "Bad method type"}, status=HTTPStatus.METHOD_NOT_ALLOWED)

@csrf_exempt
def forgot_password(request):
    if request.method == "POST":
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        try:
            user = UserInformation.objects.get(email=email, phone=phone)
            if (user.email==email) and (user.phone==phone) :
                send_otp(user)
                return JsonResponse(data={"message": 'send you otp'}, status=HTTPStatus.OK)
        except Exception:
            return JsonResponse(data={"message": "User does not exist"}, status=HTTPStatus.BAD_REQUEST)
    else:
        return JsonResponse(data={"message": "Bad method type"}, status=HTTPStatus.METHOD_NOT_ALLOWED)
