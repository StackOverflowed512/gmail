from fastapi import FastAPI, HTTPException, status, APIRouter, Depends , Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import dns.resolver
from fastapi.responses import StreamingResponse
from mail.Auth import Auth
from mail.mails import Mail
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer

# Secret key and JWT configuration
SECRET_KEY = "mailaiv1bycodexuln232412"  # Change this to a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

# Enable CORS for all origins (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Pydantic Models
# ---------------------------

class LoginProps(BaseModel):
    email: str
    password: str

class MailByUid(BaseModel):
    uid: str

class ResponseProps(BaseModel):
    data: str

class EmailProps(BaseModel):
    subject: str
    body: str
    to: str

# ---------------------------
# Utility Functions
# ---------------------------

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Create a JWT access token with the provided data and expiration.
    """
    print("create_access_token")
    to_encode = data.copy()
    print(to_encode)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ---------------------------
# Authentication Endpoints
# ---------------------------

@app.post("/login")
async def login(props: LoginProps):
    """
    User login endpoint.
    Validates credentials and returns a JWT token with mail server info.
    """
    email, password = props.email, props.password
    auth = Auth(email, password)
    try:
        login = await auth.login()
        if not login["login"]:
            print("Login failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Login failed"
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": email,
                "password": password,
                "smtpHost": login["SMTPHost"],
                "imapHost": login["IMAPHost"],
                "smtpPort": login["SMTPPort"],
                "imapPort": login["IMAPPort"],
            },
            expires_delta=access_token_expires,
        )
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        print("error main", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Login failed"
        )

# ---------------------------
# Protected API Router
# ---------------------------

protected_router = APIRouter()

@protected_router.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    """
    Example protected route.
    Returns user and mail server info if token is valid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        password: str = payload.get("password")
        smtpHost: str = payload.get("smtpHost")
        imapHost: str = payload.get("imapHost")
        smtpPort: str = payload.get("smtpPort")
        imapPort: str = payload.get("imapPort")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return {
            "email": email,
            "password": password,
            "smtpHost": smtpHost,
            "imapHost": imapHost,
            "smtpPort": smtpPort,
            "imapPort": imapPort,
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

@protected_router.get("/current_user")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Returns the current user's credentials and mail server info.
    """
    print("get_current_user")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        email: str = payload.get("sub")
        password: str = payload.get("password")
        smtpHost: str = payload.get("smtpHost")
        imapHost: str = payload.get("imapHost")
        smtpPort: str = payload.get("smtpPort")
        imapPort: str = payload.get("imapPort")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return {
            "email": email,
            "password": password,
            "smtpHost": smtpHost,
            "imapHost": imapHost,
            "smtpPort": smtpPort,
            "imapPort": imapPort,
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

@protected_router.get("/inbox")
async def getmails(
    token: str = Depends(oauth2_scheme), page: int = 1, per_page: int = 10
):
    """
    Fetch paginated inbox emails for the authenticated user.
    """
    print("getmails")
    print(page, per_page)
    try:
        # Decode JWT token and extract credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        password: str = payload.get("password")
        smtpHost: str = payload.get("smtpHost")
        imapHost: str = payload.get("imapHost")
        smtpPort: str = payload.get("smtpPort")
        imapPort: str = payload.get("imapPort")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        try:
            # Initialize Mail instance and fetch emails
            auth = Mail(email, password, smtpHost, imapHost, smtpPort, imapPort)
            mails = auth.getmails(page, per_page)
            return mails
        except Exception as mail_error:
            # Handle specific mail-related errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching mails: {str(mail_error)}",
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

@protected_router.post("/mail")
async def get_mail_by_uid(props: MailByUid, token: str = Depends(oauth2_scheme)):
    """
    Fetch a specific email by UID for the authenticated user.
    """
    print("get_mail_by_uid")
    print(props.uid)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        password: str = payload.get("password")
        smtpHost: str = payload.get("smtpHost")
        imapHost: str = payload.get("imapHost")
        smtpPort: str = payload.get("smtpPort")
        imapPort: str = payload.get("imapPort")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        try:
            auth = Mail(email, password, smtpHost, imapHost, smtpPort, imapPort)
            mail = auth.get_mail_by_uid(props.uid)
            return mail
        except Exception as mail_error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching mail: {str(mail_error)}",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

# ---------------------------
# AI Integration
# ---------------------------

from ai.response_generator import FastEmailResponseGenerator
from ai.response_predictor import ResponsePredictor

# Instantiate the AI response generator and predictor.
# You can customize these parameters or load from config/env for flexibility.
generator = FastEmailResponseGenerator(
    model_name="mistral:7b-instruct-q4_K_M",
    max_tokens=250,
    temperature=0.7,
    streaming=True,
    # emotion_prompt="Custom emotion prompt if needed",
    # response_prompt="Custom response prompt if needed",
    # response_human_template="Custom human template if needed"
)

predictor = ResponsePredictor(
    model_name="mistral:7b-instruct-q4_K_M",
    temperature=0.7,
    max_tokens=200,
    streaming=True,
    # system_prompt="Custom system prompt if needed",
    # human_prompt_template="Custom human template if needed"
)

@app.post("/response")
async def generate_email_response(request: Request):
    try:
        data = await request.json()
        email_content = data.get("data")
        
        if not email_content:
            raise HTTPException(status_code=400, detail="Email content is required")

        # Detect emotion first
        emotion = await generator.detect_emotion(email_content)
        
        # Get the response stream
        response_stream = generator.stream_email_response(email_content, emotion)
        
        return StreamingResponse(
            response_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict")
async def predict_reply(payload: dict):
    """
    Predict the most likely reply to an email conversation using AI.
    Streams the prediction as plain text.
    """
    return predictor.stream_reply_prediction(
        original_email=payload["original_email"],
        our_response=payload["our_response"]
    )

# ---------------------------
# Email Sending and Sent Mail Endpoints
# ---------------------------

@protected_router.post("/send")
async def send_email(
    props: EmailProps, token: str = Depends(oauth2_scheme)
):
    """
    Send an email using the authenticated user's credentials.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        password: str = payload.get("password")
        smtpHost: str = payload.get("smtpHost")
        imapHost: str = payload.get("imapHost")
        smtpPort: str = payload.get("smtpPort")
        imapPort: str = payload.get("imapPort")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        try:
            auth = Mail(email, password, smtpHost, imapHost, smtpPort, imapPort)
            await auth.send_email( props.to ,props.subject, props.body , )
            return {"status": "Email sent successfully"}
        except Exception as mail_error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error sending email: {str(mail_error)}",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

@protected_router.get("/sentbox")
async def get_sent_mails(
    token: str = Depends(oauth2_scheme), page: int = 1, per_page: int = 10
):
    """
    Fetch paginated sent emails for the authenticated user.
    """
    print("get_sent_mails")
    print(page, per_page)
    try:
        # Decode JWT token and extract credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        password: str = payload.get("password")
        smtpHost: str = payload.get("smtpHost")
        imapHost: str = payload.get("imapHost")
        smtpPort: str = payload.get("smtpPort")
        imapPort: str = payload.get("imapPort")
        print(email, password, smtpHost, imapHost, smtpPort, imapPort)
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        try:
            # Initialize Mail instance and fetch sent emails
            auth = Mail(email, password, smtpHost, imapHost, smtpPort, imapPort)
            sent_mails = auth.get_sent_mails(page, per_page)
            return sent_mails
        except Exception as mail_error:
            # Handle specific mail-related errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching sent mails: {str(mail_error)}",
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

@protected_router.post("/sent_mail")
async def get_sent_mail_by_uid(props: MailByUid, token: str = Depends(oauth2_scheme)):
    """
    Fetch a specific sent email by UID for the authenticated user.
    """
    print("get_sent_mail_by_uid")
    print(props.uid)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        password: str = payload.get("password")
        smtpHost: str = payload.get("smtpHost")
        imapHost: str = payload.get("imapHost")
        smtpPort: str = payload.get("smtpPort")
        imapPort: str = payload.get("imapPort")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        try:
            auth = Mail(email, password, smtpHost, imapHost, smtpPort, imapPort)
            sent_mail = auth.get_sent_mail_by_uid(props.uid)
            return sent_mail
        except Exception as mail_error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching sent mail: {str(mail_error)}",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

# ---------------------------
# FastAPI App Startup
# ---------------------------

# Register the protected router with the main app
app.include_router(protected_router)

if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI app with Uvicorn server
    uvicorn.run("main:app", host="0.0.0.0" , port=7000, reload=True , workers=8)
