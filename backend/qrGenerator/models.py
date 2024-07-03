from mongoDB_connection import mongoDb
from pydantic import BaseModel, Field, validator, ValidationInfo
from typing import Optional


# MongoDB collections
qr_collection = mongoDb['QRs']


class Customizations(BaseModel):
    name: str
    border_color: str
    qr_code_size: str

class ScanMeCustomization(BaseModel):
    text: str
    height: str
    font_size: str
    color: str
    background_color: str

class AdvancedOptions(BaseModel):
    qr_color: str
    qr_type: str
    eye_radius: str

class QRValidator(BaseModel):
    url: str
    customizations: Customizations
    scan_me_customization: ScanMeCustomization
    advanced_options: AdvancedOptions