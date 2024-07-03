import json

def extract_form_update(request):
    customizations = None
    scan_me_customization = None
    advanced_options = None
    
    customizations_str = request.POST.get('customizations')
    if customizations_str is not None:
        customizations = json.loads(customizations_str)
    else:
        customizations = None
    
    
    scan_me_customization_str = request.POST.get('scan_me_customization')
    if scan_me_customization_str is not None:
        scan_me_customization = json.loads(scan_me_customization_str)
    else:
        scan_me_customization = None
    
    
    advanced_options_str = request.POST.get('advanced_options')
    if advanced_options_str is not None:
        advanced_options = json.loads(advanced_options_str)
    else:
        advanced_options = None
    
    url = request.POST.get('url')
    logo = request.FILES.get('logo')
    qr = request.FILES.get('qr')

    data = {
        "others": {
            "url": url,
            "customizations": customizations,
            "scan_me_customization": scan_me_customization,
            "advanced_options": advanced_options
        },
        "logo": logo,
        "qr": qr
    }
    return data
