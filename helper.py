import requests
import json
from django.shortcuts import HttpResponseRedirect, reverse
SUCCESS, FAILED = 1, 2


def safe_hit_url(url, payload=None, headers=None, timeout=10):
    """
        Function to safely HIT an API with all exceptions being handled.
    """
    org = "Github"
    try:
        r = requests.get(url, params=payload, headers=headers, timeout=timeout)
        print(f"\n\nHeaders are: {r.request.headers}")

        try:
            response_data = r.json()
            return {
                "status": SUCCESS,
                "data": response_data
            }
        except json.decoder.JSONDecodeError:
            error_str = f"Internal Server Error: Could not fetch data. Probably {org} Server is down. Try again!"
            return {
                "status": FAILED,
                "message": error_str,
            }
    except requests.exceptions.ConnectTimeout:
        error_str = f"ConnectTimeout: Could not connect to {org} server. Check your Internet Connection and Try Again!"
        return {
            "status": FAILED,
            "message": error_str,
        }
    except requests.exceptions.ReadTimeout:
        error_str = f"ReadTimeout: Connected to {org} server but it took too long to respond. Try Again!"
        return {
            "status": FAILED,
            "message": error_str,
        }
    except requests.exceptions.ConnectionError:
        error_str = f"ConnectTimeout: Could not connect to {org} server. Check your Internet Connection and Try Again!"
        return {
            "status": FAILED,
            "message": error_str,
        }


def complete_profile_required(func):
    """
    A decorator which checks if the profile is complete or not.
    In case the profile is not complete, user is directed to Complete Profile Page.
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        request = args[0]
        user = request.user
        if user.is_authenticated and (not user.userprofile.is_complete):
            return HttpResponseRedirect(reverse('complete_profile'))
        return func(*args, **kwargs)

    return wrapper
