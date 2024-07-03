import json

def extract_form(request):
    invoiceFormData = json.loads(request.POST.get('invoiceFormData'))
    invoiceItemsData = json.loads(request.POST.get('invoiceItemsData'))
    selectedTax = request.POST.get('selectedTax')
    totalBefore = request.POST.get('totalBefore')
    totalAfter = request.POST.get('totalAfter')
    totalVat = request.POST.get('totalVat')
    color = request.POST.get('color')
    selectedCurrency = json.loads(request.POST.get('selectedCurrency'))
    companyLogo = request.FILES.get('companyLogo')
    signature = request.FILES.get('signature')
    invoiceImage = request.FILES.get('invoiceImage')
    bankDetails = json.loads(request.POST.get('bankDetails'))

    data = {
        "others": {
            "invoiceFormData": invoiceFormData,
            "invoiceItemsData":invoiceItemsData,
            "selectedTax":selectedTax,
            "totalBefore":totalBefore,
            "totalAfter":totalAfter,
            "totalVat":totalVat,
            "color":color,
            "selectedCurrency":selectedCurrency,
            "bankDetails":bankDetails
        },
        "companyLogo": companyLogo,
        "signature": signature,
        "invoiceImage": invoiceImage,
    }
    return data

        