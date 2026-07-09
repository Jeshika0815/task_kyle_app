from fastapi import APIRouter, HTTPException, status, Depends
from app.auth_relation import token_verification as token_veri
import app.prompt_listing as ppl
from app.auth_relation import get_http_client
import app.auth_relation as auth

router = APIRouter(
    prefix="/prompt_ctl",
    dependencies=[Depends(token_veri)]
)

@router.post("/prompt_analyze")
def prompt_analyze(prompt: str, id_token: str, client: auth.httpx.AsyncClient = Depends(get_http_client)):
    user_info = token_veri(id_token, client=client)
    if user_info is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You need authorize this service")

    result = ppl.p_listing(prompt)

    return result
