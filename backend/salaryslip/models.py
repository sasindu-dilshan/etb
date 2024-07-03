from datetime import datetime
from mongoDB_connection import mongoDb
from typing import List, Optional, Dict
from pydantic import BaseModel, validator

# MongoDB invoice collection
salaryslip_collection = mongoDb['SalarySlip']


#!#################### VALIDATORS ##########################################
#!##########################################################################



##################! start: currency validation ############################################
class CurrencyValidator(BaseModel):
    name: str
    symbol: str
    flag: str
# ##################! end: currency validation ##############################################


# ##################! start: header value validation ########################################
class HeaderValuesValidator(BaseModel):
    companyName: str
    companyAddress1: str
    companyAddress2: str
    employeeName: str
    employeeId: str
    taxCode: str
    payStart: str
    payEnd: str

    @validator("payStart", "payEnd")
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in the format YYYY-MM-DD")
        return v
# ##################! end: header value validation ##########################################



# ##################! start: footer value validation ########################################
class FooterValuesValidator(BaseModel):
    payDate: str
    designation: str

    @validator("payDate")
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in the format YYYY-MM-DD")
        return v
# ##################! end: header value validation ##########################################




# ##################! start: earning item validation ########################################
class EarningItemValidator(BaseModel):
    id: int
    description: str
    hourlyRate: Optional[float] = None
    hours: float
    fixedPayment: Optional[float] = None
    payment: float
# ##################! end: earning item validation ##########################################




# ##################! start: deduction item validation ######################################
class DeductionItemValidator(BaseModel):
    id: str
    description: str
    payment: float
# ##################! end: deduction item validation ########################################




# ##################! start: totals validation ##############################################


class TotalsValidator(BaseModel):
    totalEarnings: float
    totalDeductions: float
    netPay: float
# ##################! end: totals validation ################################################





# ##################! start: salary slip validation #########################################
class SalarySlipValidator(BaseModel):
    headerValues: HeaderValuesValidator
    footerValues: FooterValuesValidator
    earningItems: List[EarningItemValidator]
    deductionItems: List[DeductionItemValidator]
    selectedCurrency: CurrencyValidator
    color: str
    totals: TotalsValidator
    unique_uuid: str
    user_id: str
    isFixedPayment: Optional[bool] = False
    companyLogo: Optional[Dict] = None
    signature: Optional[Dict] = None
    slipImage: Optional[Dict] = None

# ##################! end: salary slip validation ###########################################













