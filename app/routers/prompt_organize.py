from fastapi import APIRouter, HTTPException, status, Depends
import app.prompt_listing as ppl
from .. import models
from ..auth_relation import auth_verification

router = APIRouter(
    prefix="/prompt_ctl",
    tags=["prompt_ctl"]
)

@router.post("/prompt_analyze")
def prompt_analyze(prompt: str, current_user: models.Users = Depends(auth_verification)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authenticated yet")

    result = ppl.p_listing(prompt)

    return result
