from pydantic import BaseModel, EmailStr
from typing import List, Optional




class InvoiceItemValidator(BaseModel):
    description: Optional[str] = None
    quantity: Optional[int] = None
    unitPrice: Optional[float] = None
    total: Optional[float] = None

class InvoiceFormDataValidator(BaseModel):
    companyName: Optional[str] = None
    companyAddressLine1: Optional[str] = None
    companyAddressLine2: Optional[str] = None
    companyEmail: Optional[EmailStr] = None 
    companyPhoneNumber: Optional[str] = None
    clientName: Optional[str] = None
    clientAddressLine1: Optional[str] = None
    clientAddressLine2: Optional[str] = None
    clientEmail: Optional[EmailStr] = None
    clientPhoneNumber: Optional[str] = None
    invoiceNumber: Optional[str] = None
    invoiceDate: Optional[str] = None
    dueDate: Optional[str] = None
    message: Optional[str] = None
    terms: Optional[str] = None

class BankDetailsValidator(BaseModel):
    name: Optional[str] = None
    accountName: Optional[str] = None
    accountNumber: Optional[str] = None
    branchBic: Optional[str] = None
    additionalDetails: Optional[str] = None

class InvoiceValidator(BaseModel):
    invoiceFormData: InvoiceFormDataValidator
    invoiceItemsData: List[InvoiceItemValidator]
    bankDetails: BankDetailsValidator
    selectedTax: Optional[str] = None
    totalBefore: Optional[float] = None
    totalAfter: Optional[float]
    totalVat: Optional[float]
    color: Optional[str]
    logo: Optional[str] = None
    signature: Optional[str] = None
    selectedCurrency: Optional[str] = None
    unique_uuid: str
    user_id: str