from fastapi import APIRouter, Depends, Form
from .. import prompt_listing as ppl
from ..auth_relation import get_current_user

router = APIRouter(
    prefix="/prompt_ctl",
    dependencies=[Depends(get_current_user)],
    tags=["prompt_ctl"],
)

@router.post("/prompt_analyze")
def prompt_analyze(prompt: str = Form(...)):
    return ppl.p_listing(prompt)
