from mongoDB_connection import mongoDb
from pydantic import BaseModel, validator
from typing import List


# MongoDB collections
tools_collection = mongoDb['Tools']


class ToolValidator(BaseModel):
    feature_name: str
    allowed: List[str]

    @validator('feature_name')
    def feature_name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Feature name cannot be empty')
        return v

    @validator('allowed', each_item=True)
    def allowed_values(cls, v):
        valid_values = {'guest', 'free', 'pro', 'premium', 'all'}
        if v not in valid_values:
            raise ValueError(f'Invalid value "{v}" in allowed list. Allowed values are: {valid_values}')
        return v


class ToolsValidator(BaseModel):
    tool_name: str
    allowed: List[str]
    features: List[ToolValidator]

    @validator('tool_name')
    def tool_name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Tool name cannot be empty')
        return v
    
    @validator('allowed', each_item=True)
    def allowed_values(cls, v):
        valid_values = {'guest', 'free', 'pro', 'premium', 'all'}
        if v not in valid_values:
            raise ValueError(f'Invalid value "{v}" in allowed list. Allowed values are: {valid_values}')
        return v
