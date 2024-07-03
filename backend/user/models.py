import bcrypt
from mongoDB_connection import mongoDb
from pydantic import BaseModel, EmailStr, validator


# MongoDB collections
user_collection = mongoDb['User']


class UserValidator(BaseModel):
    username: str
    password: str
    email: EmailStr
    phone_number: str

    @validator('password')
    def password_length(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
import uuid

class UserAccountManager(BaseUserManager):
    def create_user(self, email, username, name=None, phone_number=None, plan=None, auth_level='free', unique_uuid_user=None, dp=None, password=None):
        if not (email and username):
            raise ValueError("Users must have an email address and a username")

        if unique_uuid_user is None:
            unique_uuid_user = str(uuid.uuid4())
        
        if plan is None:
            plan = 'free'

        if dp is None:
            dp = {
                "dp_id": str(unique_uuid_user),
                "dp_url":""
            }

        user = self.model(
            username=username,
            email=email,
            name=name,
            phone_number=phone_number,
            plan=plan,
            auth_level=auth_level,
            unique_uuid_user=unique_uuid_user,
            dp=dp,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    username = models.CharField(
        verbose_name="username",
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator()],
    )
    name = models.CharField(max_length=150, blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    plan = models.CharField(max_length=10, default='free')
    auth_level = models.CharField(max_length=10, default='user')
    unique_uuid_user = models.CharField(max_length=36, unique=True)
    dp = models.JSONField(default=dict)

    objects = UserAccountManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def set_password(self, raw_password):
        if raw_password is not None:
            self.password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
        else:
            self.set_unusable_password()

    def check_password(self, raw_password):
        return bcrypt.checkpw(raw_password.encode('utf-8'), self.password.encode('utf-8'))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)