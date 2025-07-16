from pydantic import BaseModel

class ProductResponse(BaseModel): # No leading spaces here
    product_name: str
    mention_count: int

class ChannelActivityResponse(BaseModel): # No leading spaces here
    date: str
    message_count: int