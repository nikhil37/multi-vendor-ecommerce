from django.conf import settings
import re

MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)
def add_company_details(request):
    ret_dict = {
        "currency": settings.CURRENCY,
        "razor_api_key":settings.RAZOR_API_KEY,
    }
    return ret_dict
