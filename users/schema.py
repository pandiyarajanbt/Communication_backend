import random
from datetime import timedelta

import graphene
from django.core.mail import send_mail
from django.utils import timezone
from graphene_django import DjangoObjectType
from graphql_jwt.shortcuts import get_token

from users.models.users import User


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'phone',
            'address',
            'city',
            'country',
            'postal_code',
            'state',
            'role',
        )


class RegisterUserMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        username = graphene.String()
        phone = graphene.String()
        address = graphene.String()
        city = graphene.String()
        country = graphene.String()
        postal_code = graphene.String()
        state = graphene.String()

    token = graphene.String()
    user = graphene.Field(UserType)

    @classmethod
    def mutate(
        cls,
        root,
        info,
        email,
        password,
        username=None,
        phone='',
        address='',
        city='',
        country='',
        postal_code='',
        state='',
    ):
        email = (email or '').strip()
        if not email:
            raise ValueError('Email is required.')
        if User.objects.filter(email__iexact=email).exists():
            raise ValueError('A user with this email already exists.')
        if len(password or '') < 8:
            raise ValueError('Password must be at least 8 characters long.')

        user = User.objects.create_user(
            email=email,
            username=username or email,
            password=password,
            phone=phone or '',
            address=address or '',
            city=city or '',
            country=country or '',
            postal_code=postal_code or '',
            state=state or '',
        )
        return cls(token=get_token(user), user=user)


class SendOtpMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)

    @classmethod
    def mutate(cls, root, info, email):
        email = (email or '').strip()
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            raise ValueError('User not found.')

        otp_code = str(random.randint(100000, 999999)).zfill(6)
        user.otp_code = otp_code
        user.otp_created_at = timezone.now()
        user.save(update_fields=['otp_code', 'otp_created_at'])

        send_mail(
            subject='Your OTP Code',
            message=f'Your login OTP is: {otp_code}. It is valid for 5 minutes.',
            from_email='hello@daynus.space',
            recipient_list=[user.email],
            fail_silently=False,
        )

        return cls(
            success=True,
            message='OTP generated successfully and sent to your email.',
            user=user,
        )


class LoginUserMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String()
        otp = graphene.String()

    token = graphene.String()
    user = graphene.Field(UserType)

    @classmethod
    def mutate(cls, root, info, email, password=None, otp=None):
        email = (email or '').strip()
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            raise ValueError('Invalid email address.')

        if password is not None:
            if not user.check_password(password):
                raise ValueError('Invalid password.')
            return cls(token=get_token(user), user=user)

        if otp is not None:
            if not user.otp_code or not user.otp_created_at:
                raise ValueError('No OTP generated for this user.')
            if timezone.now() > user.otp_created_at + timedelta(minutes=5):
                user.otp_code = None
                user.otp_created_at = None
                user.save(update_fields=['otp_code', 'otp_created_at'])
                raise ValueError('OTP has expired.')
            if str(otp).strip() != str(user.otp_code).strip():
                raise ValueError('Invalid OTP.')

            user.otp_code = None
            user.otp_created_at = None
            user.save(update_fields=['otp_code', 'otp_created_at'])
            return cls(token=get_token(user), user=user)

        raise ValueError('Provide either password or otp.')
