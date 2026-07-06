from fastapi import APIRouter, HTTPException, status
import app.auth_relation as auth
import app.prompt_listing as ppl

router = APIRouter()

@router.post("/prompt_analyze")
async def prompt_analyze(prompt: str, id_token: str):
    user_info = await auth.token_verification(id_token)
    if user_info is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You need authorize this service")

    result = ppl.p_listing(prompt)

    return result
