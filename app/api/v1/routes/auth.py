from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.blacklisted_token import BlacklistedToken
from app.services.auth.jwt_handler import create_access_token, decode_access_token, create_refresh_token, decode_refresh_token
from app.services.auth.otp_handler import OTPHandler
from app.schemas.auth_schema import (
    RequestOTPRequest,
    RequestOTPResponse,
    VerifyOTPRequest,
    VerifyOTPResponse,
    TokenResponse,
    RefreshRequest,
    LogoutResponse
)

router = APIRouter(prefix="/auth", tags=["Auth"])


# Request OTP endpoint
@router.post("/request-otp", response_model=RequestOTPResponse, operation_id="requestOtpApi")
def request_otp(request: RequestOTPRequest, db: Session = Depends(get_db)):
    """Request an OTP to be sent to the user's email or phone"""

    # Check if user exists
    user = OTPHandler.get_user_by_identifier(request.identifier, db)
    identifier_type = OTPHandler.get_identifier_type(request.identifier)

    if not user:
        # Create a temporary user record for OTP purposes
        # This will be used to store the OTP temporarily
        if identifier_type == "email":
            user = User(
                name="",  # Will be updated during verification
                email=request.identifier,
                phone_number=None,
                role=UserRole.user
            )
        else:
            user = User(
                name="",  # Will be updated during verification
                email=None,
                phone_number=request.identifier,
                role=UserRole.user
            )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Create OTP
    otp = OTPHandler.create_otp(user.id)

    # Send OTP message to RabbitMQ
    success = OTPHandler.send_otp_message(request.identifier, otp["code"], identifier_type)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to send OTP message")

    return RequestOTPResponse(
        message=f"OTP sent successfully to your {identifier_type}",
        identifier_type=identifier_type
    )


# Verify OTP endpoint (merges signup and login logic)
@router.post("/verify-otp", response_model=VerifyOTPResponse, operation_id="verifyOtpApi")
def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """Verify OTP and authenticate user. Creates new user if doesn't exist."""

    # Get user by identifier
    user = OTPHandler.get_user_by_identifier(request.identifier, db)
    identifier_type = OTPHandler.get_identifier_type(request.identifier)

    if not user:
        raise HTTPException(status_code=400, detail="User not found. Please request OTP first.")

    # Validate OTP
    if not OTPHandler.validate_otp(user.id, request.otp_code):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Check if this is a new user (empty name indicates new user)
    is_new_user = user.name == "" or user.name is None

    # For new users, we don't require name during OTP verification
    # Users can add their name later through profile update
    if is_new_user:
        # Keep the temporary name for now, user can update it later
        pass

    # Generate tokens
    access_token = create_access_token({
        "user_id": user.id,
        "email": user.email,
        "phone_number": user.phone_number
    })
    refresh_token = create_refresh_token({
        "user_id": user.id
    })

    return VerifyOTPResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        is_new_user=is_new_user
    )


# Check current user
@router.post("/check-user", operation_id="checkUserApi", include_in_schema=False)
def check_user(
    access_token: str = Header(..., description="Access token (without Bearer)"),
    db: Session = Depends(get_db)
):
    if access_token.startswith("Bearer "):
        access_token = access_token.replace("Bearer ", "")
    payload = decode_access_token(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    # Check if token is blacklisted
    if db.query(BlacklistedToken).filter_by(token=access_token).first():
        raise HTTPException(status_code=401, detail="Token blacklisted")
    return {"msg": "Token is valid"}


# Refresh token
@router.post("/refresh", response_model=TokenResponse, operation_id="refreshTokenApi")
def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_refresh_token(request.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if db.query(BlacklistedToken).filter_by(token=request.refresh_token).first():
        raise HTTPException(status_code=401, detail="Token Blacklisted")

    user_id = payload["user_id"]
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token = create_access_token({
        "user_id": user.id,
        "email": user.email,
        "phone_number": user.phone_number
    })
    refresh_token = create_refresh_token({"user_id": user.id})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


# Logout
@router.post("/logout", response_model=LogoutResponse, operation_id="logoutApi")
def logout(
    access_token: str = Header(..., description="Access token (without Bearer)"),
    db: Session = Depends(get_db)
):
    if access_token.startswith("Bearer "):
        access_token = access_token.replace("Bearer ", "")

    payload = decode_access_token(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    db.add(BlacklistedToken(user_id=payload["user_id"], token=access_token))
    db.commit()
    return {"msg": "Token blacklisted successfully"}

