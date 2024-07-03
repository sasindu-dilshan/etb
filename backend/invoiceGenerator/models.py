from mongoDB_connection import mongoDb
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict



# MongoDB invoice collection
invoice_collection = mongoDb['Invoice']


class CurrencyValidator(BaseModel):
    name: str
    symbol: str
    flag: str


class InvoiceItemValidator(BaseModel):
    description: str
    quantity: int
    unitPrice: float
    total: float

class InvoiceFormDataValidator(BaseModel):
    companyName: str
    companyAddressLine1: str
    companyAddressLine2: str
    companyEmail: EmailStr
    companyPhoneNumber: str
    clientName: str
    clientAddressLine1: str
    clientAddressLine2: str
    clientEmail: EmailStr
    clientPhoneNumber: str
    invoiceNumber: str
    invoiceDate: str
    dueDate: str
    message: str
    terms: str


class BankDetailsValidator(BaseModel):
    name: str
    accountName: str
    accountNumber: str
    branchBic: str
    additionalDetails: str

class InvoiceValidator(BaseModel):
    invoiceFormData: InvoiceFormDataValidator
    invoiceItemsData: List[InvoiceItemValidator]
    bankDetails: BankDetailsValidator
    selectedTax: str
    totalBefore: float
    totalAfter: float
    totalVat: float
    color: str
    companyLogo: Optional[Dict] = None
    signature: Optional[Dict] = None
    invoiceImage: Optional[Dict] = None
    selectedCurrency: CurrencyValidator
    unique_uuid: str
    user_id: str