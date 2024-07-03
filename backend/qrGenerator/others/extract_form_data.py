import json

def extract_form(request):
    url = request.POST.get('url')
    customizations = json.loads(request.POST.get('customizations'))
    scan_me_customization = json.loads(request.POST.get('scan_me_customization'))
    advanced_options = json.loads(request.POST.get('advanced_options'))
    logo = request.FILES.get('logo')
    qr = request.FILES.get('qr')

    data = {
        "others": {
            "url": url,
            "customizations":customizations,
            "scan_me_customization":scan_me_customization,
            "advanced_options":advanced_options
        },
        "logo": logo,
        "qr": qr
    }
    return data

        