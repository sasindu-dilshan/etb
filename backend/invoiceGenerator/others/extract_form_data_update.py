import json

def extract_form_update(request):
    invoice_form_data = None
    invoice_items_data = None
    selected_currency = None
    bankDetails = None
    
    invoice_form_data_str = request.POST.get('invoiceFormData')
    if invoice_form_data_str is not None:
        invoice_form_data = json.loads(invoice_form_data_str)
    else:
        invoice_form_data = None
    
    

    invoice_items_data_str = request.POST.get('invoiceItemsData')
    if invoice_items_data_str is not None:
        invoice_items_data = json.loads(invoice_items_data_str)
    else:
        invoice_items_data = None
    
    
    selected_currency_str = request.POST.get('selectedCurrency')
    if selected_currency_str is not None:
        selected_currency = json.loads(selected_currency_str)
    else:
        selected_currency = None
    
    bankDetails_str = request.POST.get('bankDetails')
    if bankDetails_str is not None:
        bankDetails = json.loads(bankDetails_str)
    else:
        bankDetails = None

    selected_tax = request.POST.get('selectedTax')
    total_before = request.POST.get('totalBefore')
    total_after = request.POST.get('totalAfter')
    total_vat = request.POST.get('totalVat')
    color = request.POST.get('color')

    companyLogo = request.FILES.get('companyLogo')
    signature = request.FILES.get('signature')
    invoiceImage = request.FILES.get('invoiceImage')

    data = {
        "others": {
            "invoiceFormData": invoice_form_data,
            "invoiceItemsData": invoice_items_data,
            "selectedTax": selected_tax,
            "totalBefore": total_before,
            "totalAfter": total_after,
            "totalVat": total_vat,
            "color": color,
            "selectedCurrency": selected_currency,
            "bankDetails": bankDetails
        },
        "companyLogo": companyLogo,
        "signature": signature,
        "invoiceImage": invoiceImage
    }
    return data
