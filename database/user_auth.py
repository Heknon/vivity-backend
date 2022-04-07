from __future__ import annotations

import datetime
import time

import pyotp
from bson import ObjectId
from pymongo import ReturnDocument

import database.user.user as user_module
from database import DocumentObject, user_auth_collection


class UserAuth(DocumentObject):
    LONG_TO_SHORT = {
        "_id": "_id",
        "attempts": "atmps",
        "last_attempt_time": "lat",
        "otp_secret": "otp",
        "blocked_otp": "botp",
        "blocked_otp_time": "botp_t"
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            _id: ObjectId,
            attempts: int,
            last_attempt_time: datetime.datetime,
            otp_secret: str,
            blocked_otp: str,
            blocked_otp_time: datetime.datetime,
    ):
        self._id = _id
        self.attempts = attempts
        self.last_attempt_time = last_attempt_time
        self.otp_secret = otp_secret if UserAuth.is_otp_secret(otp_secret) else None
        self.blocked_otp = blocked_otp
        self.blocked_otp_time = blocked_otp_time

        self.has_2fa = otp_secret is not None
        self.totp = pyotp.totp.TOTP(otp_secret) if self.has_2fa else None

    def validate_attempt_range(self, max_attempts: int = 5, max_attempts_cooldown: datetime.timedelta = datetime.timedelta(minutes=5)):
        if self.attempts >= max_attempts \
                and datetime.datetime.now() < (self.last_attempt_time + max_attempts_cooldown):
            return False

        return True

    def should_reset_attempts(self, max_attempts: int = 5, max_attempts_cooldown: datetime.timedelta = datetime.timedelta(minutes=5)):
        if self.attempts >= max_attempts \
                and datetime.datetime.now() > (self.last_attempt_time + max_attempts_cooldown):
            return True

        return False

    def is_correct_otp(self, otp: str):
        if not self.has_2fa:
            return True

        return self.totp.now() == otp

    @staticmethod
    def reset_attempts(_id: ObjectId):
        return UserAuth.document_repr_to_object(
            user_auth_collection.find_one_and_update(
                {"_id": _id},
                {
                    "$set": {"atmps": 0},
                },
                return_document=ReturnDocument.AFTER
            )
        )

    @staticmethod
    def get_by_id(_id: ObjectId):
        return UserAuth.document_repr_to_object(
            user_auth_collection.find_one({"_id": _id})
        )

    @staticmethod
    def get_by_email(email: str):
        user = user_module.User.get_by_email(email, raw_document=False)
        if user is None:
            return None

        return UserAuth.document_repr_to_object(
            user_auth_collection.find_one({"_id": user.id})
        )

    @staticmethod
    def create_from_id(_id: ObjectId, failed_attempt: bool = False):
        user_auth_collection.insert_one(
            UserAuth.get_db_repr(
                UserAuth(_id, 1 if failed_attempt else 0, datetime.datetime.now(), None, None, None)
            )
        )

    @staticmethod
    def delete_by_id(_id: ObjectId):
        return user_auth_collection.delete_one({"_id": _id})

    @staticmethod
    def register_failed_attempt(_id: ObjectId):
        return UserAuth.document_repr_to_object(
            user_auth_collection.find_one_and_update(
                {"_id": _id},
                {
                    "$inc": {"atmps": 1},
                    "$set": {"lat": time.time()}
                },
                return_document=ReturnDocument.AFTER
            )
        )

    @staticmethod
    def register_successful_attempt(_id: ObjectId):
        return UserAuth.document_repr_to_object(
            user_auth_collection.find_one_and_update(
                {"_id": _id},
                {
                    "$set": {"atmps": 0, "lat": int(time.time())},
                },
                return_document=ReturnDocument.AFTER
            )
        )

    @staticmethod
    def block_otp(_id: ObjectId, otp: str):
        return UserAuth.document_repr_to_object(
            user_auth_collection.find_one_and_update(
                {"_id": _id},
                {
                    "$set": {"botp": otp, "botp_t": int(time.time())}
                },
                return_document=ReturnDocument.AFTER
            )
        )

    @staticmethod
    def turn_on_otp(_id: ObjectId):
        return UserAuth._update_otp_secret(_id, pyotp.random_base32())

    @staticmethod
    def turn_off_otp(_id: ObjectId):
        return UserAuth._update_otp_secret(_id, None)

    @staticmethod
    def _update_otp_secret(_id: ObjectId, secret: str):
        return UserAuth.document_repr_to_object(
            user_auth_collection.find_one_and_update(
                {"_id": _id},
                {
                    "$set": {"otp": secret, "botp": None, "botp_t": None},
                },
                return_document=ReturnDocument.AFTER
            )
        )

    @staticmethod
    def get_db_repr(user_auth: UserAuth, get_long_names: bool = False):
        res = {value: getattr(user_auth, key) for key, value in UserAuth.LONG_TO_SHORT.items()}
        res["lat"] = int(user_auth.last_attempt_time.timestamp())
        res["botp_t"] = int(user_auth.blocked_otp_time.timestamp()) if user_auth.blocked_otp_time is not None else None

        if not UserAuth.is_otp_secret(user_auth.otp_secret):
            res['otp'] = None

        if get_long_names:
            res["_id"] = str(res["_id"])
            res = {user_auth.lengthen_field_name(key): value for key, value in res.items()}

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        if doc is None:
            return None

        args = {key: doc[value] for key, value in UserAuth.LONG_TO_SHORT.items()}
        args["last_attempt_time"] = datetime.datetime.fromtimestamp(args["last_attempt_time"])
        args["blocked_otp_time"] = datetime.datetime.fromtimestamp(args["blocked_otp_time"]) if args["blocked_otp_time"] is not None else None

        if not UserAuth.is_otp_secret(args['otp_secret']):
            args['otp_secret'] = None

        return UserAuth(**args)

    @staticmethod
    def is_otp_secret(secret: str) -> bool:
        if secret is None or not isinstance(secret, str):
            return False

        try:
            totp = pyotp.totp.TOTP(secret)
            totp.now()
            return True
        except:
            return False

    def shorten_field_name(self, field_name):
        return UserAuth.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return UserAuth.SHORT_TO_LONG.get(field_name, None)
