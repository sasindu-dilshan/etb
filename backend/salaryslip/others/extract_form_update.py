import json

def extract_form__update_salary_slip(request):
    headerValues = None
    footerValues = None
    earningItems = None
    deductionItems = None
    selectedCurrency = None
    totals = None

    header_values_str = request.POST.get('headerValues')
    if header_values_str is not None:
        headerValues = json.loads(header_values_str)
    else:
        headerValues = None
    
    footer_values_str = request.POST.get('footerValues')
    if footer_values_str is not None:
        footerValues = json.loads(footer_values_str)
    else:
        footerValues = None
    
    earning_items_str = request.POST.get('earningItems')
    if earning_items_str is not None:
        earningItems = json.loads(earning_items_str)
    else:
        earningItems = None
    
    
    deduction_items_str = request.POST.get('deductionItems')
    if deduction_items_str is not None:
        deductionItems = json.loads(deduction_items_str)
    else:
        deductionItems = None
    
    
    selected_currency_str = request.POST.get('selectedCurrency')
    if selected_currency_str is not None:
        selectedCurrency = json.loads(selected_currency_str)
    else:
        selectedCurrency = None
    
    totals_str = request.POST.get('totals')
    if totals_str is not None:
        totals = json.loads(totals_str)
    else:
        totals = None

    isFixedPayment = request.POST.get('isFixedPayment')
    color = request.POST.get('color')
    companyLogo = request.FILES.get('companyLogo')
    signature = request.FILES.get('signature')
    isFixedPayment = request.POST.get('isFixedPayment')
    
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
        "signature": signature
    }
    return data

        