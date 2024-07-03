import json

def extract_form_salary_slip(request):
    headerValues = json.loads(request.POST.get('headerValues'))
    footerValues = json.loads(request.POST.get('footerValues'))
    earningItems = json.loads(request.POST.get('earningItems'))
    deductionItems = json.loads(request.POST.get('deductionItems'))
    selectedCurrency = json.loads(request.POST.get('selectedCurrency'))
    isFixedPayment = request.POST.get('isFixedPayment')
    totals = json.loads(request.POST.get('totals'))
    color = request.POST.get('color')
    isFixedPayment = request.POST.get('isFixedPayment')
    companyLogo = request.FILES.get('companyLogo')
    signature = request.FILES.get('signature')
    slipImage = request.FILES.get('slipImage')
    
    data = {
        "others": {
            "headerValues": headerValues,
            "footerValues":footerValues,
            "earningItems":earningItems,
            "deductionItems":deductionItems,
            "selectedCurrency": selectedCurrency,
            "isFixedPayment":isFixedPayment,
            "totals":totals,
            "color":color
        },
        "companyLogo": companyLogo,
        "signature": signature,
        "slipImage": slipImage
    }
    return data

        