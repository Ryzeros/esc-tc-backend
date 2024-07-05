from pydantic import BaseModel


class LoyaltyItem(BaseModel):
    program_id: str
    program_name: str
    currency_name: str
    processing_time: str
    description: str
    enrollment_link: str
    terms_link: str

    class Config:
        from_attributes = True


class LoyaltyValidate(LoyaltyItem):
    regex_pattern: str

