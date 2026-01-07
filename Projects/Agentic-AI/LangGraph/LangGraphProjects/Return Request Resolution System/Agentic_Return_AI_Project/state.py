
from typing import TypedDict, Optional

class ReturnState(TypedDict):
    input: str
    policy_result: Optional[dict]
    order_details: Optional[dict]
    decision: Optional[dict]
    response: Optional[str]
