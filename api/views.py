import json
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from sendgrid import SendGridAPIClient
from django.views.decorators.csrf import csrf_exempt
from .forms import *
from django.utils.translation import activate
from .models import UserInformation
from .mail import *


FORM_TYPE = {
    "welcome": WelcomeForm,
    "mid": MidForm,
    "closing": ClosingForm,
    "edinburgh": EdinburghForm,
    "user": UserForm,
}

import datetime
import math
import decimal


def handle_user_survey(user, daily_test=False):
    today = datetime.datetime.today().date()
    user.subscription_date = today

    # calculating
    period_date = user.due_date - datetime.timedelta(days=280)
    pregnancy_week = (today - period_date).days / 7
    pregnancy_week_round = math.floor(pregnancy_week)
    if daily_test:
        # resetting the due date after we figure out which preg week we're in
        user.due_date = today + datetime.timedelta(days=(42 - pregnancy_week_round))
    mid_days = (user.due_date - user.subscription_date).days / 2
    midterm_survey_sending_date = user.subscription_date + datetime.timedelta(
        days=mid_days
    )


    def calculate_next_mailing_date(due_date, today):
        current = due_date
        while current > today.date():
            current -= datetime.timedelta(days=7)
        return current

    if daily_test:
        next_mailing_date = today + datetime.timedelta(days=1)
    else:
        next_mailing_date = calculate_next_mailing_date(
            due_date=user.due_date,
            today=datetime.datetime.today(),
        )

    # setting
    EXTRA_REIT_DAYS = 1 if daily_test else 3

    user.last_period_date = period_date
    user.pregnancy_week = pregnancy_week
    user.pregnancy_week_round = pregnancy_week_round
    user.welcome_survey_sending_date = datetime.datetime.today()
    user.welcome_survey_reit_date = datetime.datetime.today() + datetime.timedelta(
        days=EXTRA_REIT_DAYS
    )
    user.mid_survey_sending_date = midterm_survey_sending_date
    user.mid_survey_reit_date = user.mid_survey_sending_date + datetime.timedelta(
        days=EXTRA_REIT_DAYS
    )
    user.closing_survey_sending_date = user.due_date
    user.closing_survey_reit_date = (
        user.closing_survey_sending_date + datetime.timedelta(days=EXTRA_REIT_DAYS)
    )
    user.next_mailing_date = next_mailing_date


def survey(request, type=None):
    if request.method == "GET":
        form = FORM_TYPE.get(type)
    elif request.method == "POST":
        print(request._post)
        form = FORM_TYPE.get(type)(data=request.POST)
        # print (form.__dict__) # will print more information
        if form.is_valid():
            print("Good")
            survey = form.save(False)

            if type == "user":
                handle_user_survey(user=survey, daily_test=False)
                sg = SendGridAPIClient(getattr(settings, "SENDGRID_API_KEY", None))
                sg.send(
                    create_mail(request, user_email=survey.email, email_type="welcome")
                )
            else:
                user = UserInformation.objects.get(email=form.cleaned_data["email"])
                if type == "welcome":
                    user.welcome_filled = True
                elif type == "mid":
                    user.mid_filled = True
                elif type == "closing":
                    user.closing_filled = True
                user.save()
            survey.save()
            return redirect("thank_you")
        else:
            activate("es")  # Displays errors in Spanish if browser in Spanish
            print("Fail")
            print(form.errors)
    return render(request, f"{type}_survey.html", {"survey": form})


def thank_you(request):
    return render(
        request,
        "thank_you.html",
    )


def test_newsletter(request):
    try:
        sg = SendGridAPIClient(getattr(settings, "SENDGRID_API_KEY", None))
        wk_message = create_mail(
            request,
            user_email="cee2130@columbia.edu",
            email_type="wk",
            week_num=6,
        )
        _ = sg.send(wk_message)
        survey_message = create_mail(
            request, user_email="cee2130@columbia.edu", email_type="welcome-again"
        )
        _ = sg.send(survey_message)
    except Exception as e:
        print(e.message)
        return HttpResponse(
            json.dumps({"status": "test: oh no"}),
            content_type="application/json",
        )
    else:
        return HttpResponse(
            json.dumps({"status": "test: all good"}),
            content_type="application/json",
        )


def newsletter(request):
    DAY_INCREASE_AMOUNT = 1.0 if getattr(settings, "DAILY_TEST") else 7.0
    NEXT_MAILING_DAY_INC = 1 if getattr(settings, "DAILY_TEST") else 7
    if request.method == "GET":
        try:
            sg = SendGridAPIClient(getattr(settings, "SENDGRID_API_KEY", None))
            users = UserInformation.objects.all()
            today = datetime.datetime.today().date()
            for user in users:
                if user.cancel_all:
                    pass
                elif user.complete:
                    # check one more time for closing reit email
                    message = check_for_all_surveys(request, today, user)
                    if message:
                        _ = sg.send(message)
                else:
                    user.pregnancy_week = round(
                        user.pregnancy_week + decimal.Decimal(1 / DAY_INCREASE_AMOUNT),
                        3,
                    )
                    user.pregnancy_week_round = math.floor(user.pregnancy_week)
                    user.save()

                    message = None
                    if today >= user.next_mailing_date:
                        message = create_mail(
                            request,
                            user_email=user.email,
                            email_type="wk",
                            week_num=user.pregnancy_week_round,
                        )
                        print(f"sent newsletter wk {user.pregnancy_week_round}")
                        user.next_mailing_date += datetime.timedelta(
                            days=NEXT_MAILING_DAY_INC
                        )
                        user.save()

                    if message:
                        _ = sg.send(message)

                    message = check_for_all_surveys(request, today, user)
                    if message:
                        _ = sg.send(message)

                    if user.pregnancy_week_round == 41:
                        # once all the weekly newsletters have been sent
                        user.complete = True
        except Exception as e:
            print(e.message)
            data = {"status": "oh no"}
            return HttpResponse(
                json.dumps(data),
                content_type="application/json",
            )
        else:
            data = {"status": "all good"}
            return HttpResponse(
                json.dumps(data),
                content_type="application/json",
            )


@csrf_exempt
def wordpress(request):
    response = request.POST
    try:
        phone = response.get("Celular si quieres participar de los grupos")
        if len(phone) == 0:
            pass
        elif len(phone) > 15 or len(phone) < 8:
            raise Exception
        user = UserInformation.objects.create(
            first_name=response.get("Name"),
            last_name=response.get("Last Name"),
            email=response.get("Email"),
            due_date=datetime.datetime.strptime(
                response.get("Date_parto"), "%Y-%m-%d"
            ).date(),
        )
        handle_user_survey(user, daily_test=True)
        if len(phone) == 0:
            user.save()
        else:
            user.phone = phone
            user.save()
        sg = SendGridAPIClient(getattr(settings, "SENDGRID_API_KEY", None))
        sg.send(create_mail(request, user_email=user.email, email_type="welcome"))
    except (Exception, ValueError, AttributeError) as e:
        print(e)
        data = {"status": "oh no"}
        return HttpResponse(
            json.dumps(data),
            content_type="application/json",
            status=400,
        )
    else:
        data = {"status": "all good"}
        return HttpResponse(
            json.dumps(data),
            content_type="application/json",
            status=200,
        )
