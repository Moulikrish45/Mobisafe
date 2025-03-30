from django.contrib.auth.models import User  # ✅ Import User model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import AnonRateThrottle
from django.contrib.auth import authenticate
import logging
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

class PasswordResetRateThrottle(AnonRateThrottle):
    rate = getattr(settings, 'PASSWORD_RESET_THROTTLE_RATE', '5/h')

# User registration API
@api_view(['POST'])
def register_user(request):
    """
    Register a new user with username, email, and password.
    Email is required for password reset functionality.
    """
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    # Validate required fields
    if not all([username, email, password]):
        return Response(
            {'error': 'Username, email, and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate email format
    try:
        validate_email(email)
    except ValidationError:
        return Response(
            {'error': 'Invalid email format'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if username or email already exists
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(email__iexact=email).exists():
        return Response(
            {'error': 'Email already registered'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Create user with email
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password  # create_user handles password hashing
        )
        
        logger.info(f"User registered successfully: {username}")
        return Response(
            {'message': 'User registered successfully'},
            status=status.HTTP_201_CREATED
        )
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return Response(
            {'error': 'Error creating user account'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# User login API
@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if not user:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    })

@api_view(['POST'])
@throttle_classes([PasswordResetRateThrottle])
def request_password_reset(request):
    """
    Request a password reset link.
    Expects email in request data.
    Returns success message regardless of whether email exists (for security).
    Rate limited to prevent abuse.
    """
    try:
        email = request.data.get('email')
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {'error': 'Invalid email format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find user by email (case-insensitive)
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # Don't reveal if email exists
            logger.info(f"Password reset requested for non-existent email: {email}")
            return Response(
                {'message': 'If an account exists with this email, a password reset link has been sent.'},
                status=status.HTTP_200_OK
            )

        # Generate password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Construct reset link
        reset_url = f"{settings.FRONTEND_URL}/reset-password-confirm/{uid}/{token}/"
        
        # Send email
        subject = 'Password Reset Requested - AutoIntell'
        message = f"""
        Hello {user.username},

        You requested a password reset for your AutoIntell account.
        Please click the link below to reset your password:

        {reset_url}

        This link will expire in {settings.PASSWORD_RESET_TIMEOUT // 3600} hour(s).

        If you didn't request this reset, please ignore this email and ensure your account is secure.

        Best regards,
        AutoIntell Team
        """
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            logger.info(f"Password reset email sent to {email}")
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {str(e)}")
            return Response(
                {'error': 'Failed to send password reset email. Please try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(
            {'message': 'If an account exists with this email, a password reset link has been sent.'},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        logger.error(f"Error in password reset request: {str(e)}")
        return Response(
            {'error': 'Error processing password reset request'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def confirm_password_reset(request):
    """
    Confirm password reset and set new password.
    Expects uidb64, token, new_password1, and new_password2 in request data.
    """
    try:
        uidb64 = request.data.get('uidb64')
        token = request.data.get('token')
        new_password1 = request.data.get('new_password1')
        new_password2 = request.data.get('new_password2')

        # Validate input
        if not all([uidb64, token, new_password1, new_password2]):
            return Response(
                {'error': 'Missing required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_password1 != new_password2:
            return Response(
                {'error': 'Passwords do not match'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Decode the uidb64 to get user pk
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {'error': 'Invalid reset link'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the token is valid
        if not default_token_generator.check_token(user, token):
            return Response(
                {'error': 'Invalid or expired reset link'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Set new password
        user.set_password(new_password1)
        user.save()
        
        logger.info(f"Password reset successful for user {user.username}")
        return Response(
            {'message': 'Password has been reset successfully'},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        logger.error(f"Error in password reset confirmation: {str(e)}")
        return Response(
            {'error': 'Error processing password reset confirmation'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
