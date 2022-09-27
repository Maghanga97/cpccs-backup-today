from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
import requests
from requests.structures import CaseInsensitiveDict
import json

from xhtml2pdf import pisa

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def not_null(param):
    return param != "" and param != None

def sendsms(phone, message):
    url = "https://api.mobitechtechnologies.com/sms/sendsms"
    headers = CaseInsensitiveDict()
    headers["h_api_key"] = "373a889e83bef0fda31e496b7ed5e4378e2de25fb6d2207c00a457774ff4876a"
    headers["Content-Type"] = "application/json"
    data = {"mobile" : phone,"response_type": "json","sender_name":"23107","service_id" : 0,"message" : message }
    json_data = json.dumps(data)
    resp = requests.post(url, headers=headers, data=json_data)
    return(resp.status_code)
