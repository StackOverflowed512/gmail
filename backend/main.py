from fastapi import FastAPI, HTTPException, status, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import dns.resolver
from mail.Auth import Auth
from mail.mails import Mail
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
SECRET_KEY = "your-secret-key-here"  # Change this to a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginProps(BaseModel):
    email: str
    password: str


def create_access_token(data: dict, expires_delta: timedelta = None):
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


@app.post("/login")
async def login(props: LoginProps):
    # Implement login logic
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


# protected route only accessible with a valid token
protected_router = APIRouter()


@protected_router.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
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


class MailByUid(BaseModel):
    uid: str
@protected_router.post("/mail")
async def get_mail_by_uid(props: MailByUid, token: str = Depends(oauth2_scheme)):
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
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )



class ResponseProps(BaseModel):
    data: str

from ai.response_generator import FastEmailResponseGenerator
@app.post("/response")
async def sendresponse(props: ResponseProps):
    try:
        auth = FastEmailResponseGenerator()
        response = await auth.generate_response(props.data)
        return response
    except Exception as mail_error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating response: {str(mail_error)}",
        )


from ai.response_predictor import ResponsePredictor
class PredictProps(BaseModel):
    original_email: str
    our_response: str
@app.post("/predict")
async def predict(props: PredictProps):
    try:
        auth = ResponsePredictor()
        response = await auth.predict_reply(props.original_email, props.our_response)
        return response
    except Exception as mail_error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating response: {str(mail_error)}",
        )


class EmailProps(BaseModel):
    subject: str
    body: str
    to: str

@protected_router.post("/send")
async def send_email(
    props: EmailProps, token: str = Depends(oauth2_scheme)
):
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


app.include_router(protected_router)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", port=7000, reload=True)
