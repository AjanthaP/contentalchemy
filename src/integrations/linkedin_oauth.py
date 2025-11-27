from fastapi import Header
import requests
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from src.core.config import settings

LINKEDIN_CLIENT_ID = settings.linkedin_client_id
LINKEDIN_CLIENT_SECRET = settings.linkedin_client_secret
LINKEDIN_REDIRECT_URI = settings.linkedin_redirect_uri
LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_PROFILE_URL = "https://api.linkedin.com/v2/userinfo"

router = APIRouter()

@router.get("/linkedin/login")
def linkedin_login():
    params = {
        "response_type": "code",
        "client_id": LINKEDIN_CLIENT_ID,
        "redirect_uri": LINKEDIN_REDIRECT_URI,
        "scope": "openid profile email w_member_social"
    }
    url = f"{LINKEDIN_AUTH_URL}?" + "&".join([f"{k}={v}" for k, v in params.items()])
    return RedirectResponse(url)

@router.get("/linkedin/callback")
def linkedin_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code from LinkedIn")
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": LINKEDIN_REDIRECT_URI,
        "client_id": LINKEDIN_CLIENT_ID,
        "client_secret": LINKEDIN_CLIENT_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(LINKEDIN_TOKEN_URL, data=data, headers=headers)
    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get access token")
    token = resp.json().get("access_token")
    # Optionally fetch profile info
    # profile = None
    # if token:
    #     profile_resp = requests.get(LINKEDIN_PROFILE_URL, headers={"Authorization": f"Bearer {token}"})
    #     if profile_resp.status_code == 200:
    #         profile = profile_resp.json()
    if token:
        # Redirect to frontend with token in URL
        frontend_url = "http://localhost:5173/?linkedin_token=" + token
        return RedirectResponse(frontend_url)
    return HTMLResponse("<p>LinkedIn authentication failed.</p>")


# Endpoint to post content to LinkedIn
@router.post("/linkedin/post")
async def linkedin_post(request: Request, authorization: str = Header(None)):
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
    if not token:
        raise HTTPException(status_code=401, detail="Missing LinkedIn token")
    try:
        payload = await request.json()
        content = payload.get("content")
        if not content:
            raise HTTPException(status_code=400, detail="Missing post content")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request body: {str(e)}")

    # LinkedIn post API endpoint
    post_url = "https://api.linkedin.com/v2/ugcPosts"

    # Fetch user profile to get author URN
    profile_resp = requests.get(LINKEDIN_PROFILE_URL, headers={"Authorization": f"Bearer {token}"})
    if profile_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch LinkedIn profile for posting")
    profile = profile_resp.json()
    author_urn = profile.get("sub") or profile.get("id")
    if not author_urn:
        raise HTTPException(status_code=400, detail="Missing LinkedIn author URN")
    author = f"urn:li:person:{author_urn}"

    # Prepare post payload
    post_payload = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    post_resp = requests.post(post_url, json=post_payload, headers=headers)
    if post_resp.status_code == 201:
        return {"success": True, "message": "Post published to LinkedIn."}
    else:
        return {"success": False, "error": post_resp.text, "status_code": post_resp.status_code}

# Endpoint to fetch LinkedIn profile using access token
@router.get("/linkedin/profile")
def linkedin_profile(authorization: str = Header(None)):
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
    if not token:
        raise HTTPException(status_code=401, detail="Missing LinkedIn token")
    print("LinkedIn profile url", LINKEDIN_PROFILE_URL)
    profile_resp = requests.get(LINKEDIN_PROFILE_URL, headers={"Authorization": f"Bearer {token}"})
    if profile_resp.status_code == 200:
        return {"profile": profile_resp.json()}
    # Log error details for debugging
    print("LinkedIn profile fetch failed:", profile_resp.status_code, profile_resp.text)
    raise HTTPException(status_code=400, detail=f"Failed to fetch LinkedIn profile: {profile_resp.text}")
