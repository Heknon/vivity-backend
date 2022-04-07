from __future__ import annotations

import logging
import time
from typing import List

import bcrypt
import jsonpickle
from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.results import DeleteResult
from web_framework_v2 import JwtSecurity

import database.user.cart as cart_module
import database.user.order.order_history as order_history_module
import database.user.shipping_address as shipping_address
import database.user.user_options as user_options
import database.user.liked_items as liked_items_module
from body import TokenData
from database import users_collection, DocumentObject, Image, access_token_blacklist
from database.user_auth import UserAuth

logger = logging.getLogger(__name__)


class User(DocumentObject):
    LONG_TO_SHORT = {
        "_id": "_id",
        "email": "ml",
        "name": "nm",
        "phone": "ph",
        "password": "pw",
        "options": "op",
        "shipping_addresses": "sa",
        "liked_items": "lk",
        "profile_picture": "pfp",
        "is_system_admin": "isa",
        "cart": "crt",
        "order_history": "odh",
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            _id: ObjectId,
            email: str,
            name: str,
            phone: str,
            profile_picture: Image,
            password: bytes,
            options: user_options.UserOptions,
            shipping_addresses: List[shipping_address.ShippingAddress],
            liked_items: liked_items_module.LikedItems,
            cart: cart_module.Cart,
            is_system_admin: bool,
            order_history: order_history_module.OrderHistory,
    ):
        self._id = _id
        self.email = email
        self.name = name
        self.phone = phone
        self.profile_picture = profile_picture
        self.password = password
        self.options = options
        self.shipping_addresses = shipping_addresses
        self.liked_items = liked_items
        self.cart = cart
        self.is_system_admin = is_system_admin
        self.order_history: order_history_module.OrderHistory = order_history

        self.updatable_fields = {"email", "phone", "password", "profile_picture"}

    def update_fields(self, **kwargs) -> User:
        filtered_kwargs = filter(lambda item: item[0] in self.updatable_fields, kwargs.items())
        update_dict = {
            self.shorten_field_name(key): value for key, value in filtered_kwargs
        }

        return User.document_repr_to_object(
            users_collection.find_one_and_update(
                {"_id": self._id}, {"$set": update_dict}, return_document=ReturnDocument.AFTER
            )
        )

    def insert(self) -> ObjectId:
        return users_collection.insert_one(User.get_db_repr(self)).inserted_id

    def add_address(self, address: shipping_address.ShippingAddress):
        return User.document_repr_to_object(
            users_collection.find_one_and_update(
                {"_id": self._id},
                {"$addToSet": {"sa": shipping_address.ShippingAddress.get_db_repr(address)}},
                return_document=ReturnDocument.AFTER
            )
        )

    def remove_address(self, index: int):
        users_collection.find_one_and_update(
            {"_id": self._id},
            {"$unset": {f"sa.{index}": 1}}
        )

        return User.document_repr_to_object(
            users_collection.find_one_and_update(
                {"_id": self._id},
                {"$pull": {f"sa": None}},
                return_document=ReturnDocument.AFTER
            )
        )

    def update_profile_picture(self, image: Image):
        return User.document_repr_to_object(
            users_collection.find_one_and_update(
                {"_id": self._id},
                {"$set": {f"pfp": image.image_id if image is not None else None}},
                return_document=ReturnDocument.AFTER
            )
        )

    @staticmethod
    def promote_to_business_user(_id: ObjectId, business_id: ObjectId):
        import database.user.business_user as business_user
        return business_user.BusinessUser.document_repr_to_object(
            users_collection.find_one_and_update(
                {"_id": _id},
                {"$set": {"bid": business_id}},
                return_document=ReturnDocument.AFTER
            )
        )

    @staticmethod
    def get_user_by_token_data(token_data: TokenData):
        return User.get_by_id(token_data.user_id)

    @staticmethod
    def exists_by_id(_id: ObjectId):
        return users_collection.count_documents({"_id": _id}, limit=1) == 1

    @staticmethod
    def exists_by_email(email: str):
        return users_collection.count_documents({"ml": email}, limit=1) == 1

    @staticmethod
    def get_by_email(email, raw_document=True) -> User | dict | None:
        return users_collection.find_one({"ml": email}) \
            if raw_document else User.document_repr_to_object(users_collection.find_one({"ml": email}))

    @staticmethod
    def get_by_id(_id: ObjectId, raw_document=True) -> User | dict | None:
        document = users_collection.find_one({"_id": _id})

        return document if raw_document else User.document_repr_to_object(document)

    def __repr__(self):
        return jsonpickle.encode(User.get_db_repr(self, True), unpicklable=False)

    @staticmethod
    def document_repr_to_object(doc, **kwargs) -> User | None:
        if doc is None:
            return None

        import database.user.business_user as business_user

        cls = business_user.BusinessUser if "bid" in doc else User
        args = {key: doc.get(value, None) for key, value in cls.LONG_TO_SHORT.items()}

        args["profile_picture"] = Image(doc.get("pfp", None))
        args["options"] = user_options.UserOptions.document_repr_to_object(doc["op"], _id=doc["_id"]) if doc.get("op", None) is not None else None
        args["shipping_addresses"] = list(
            map(
                lambda t: shipping_address.ShippingAddress.document_repr_to_object(t[1], _id=doc["_id"], address_index=t[0]),
                enumerate(doc.get("sa", []))
            )
        )
        args["liked_items"] = \
            liked_items_module.LikedItems.document_repr_to_object(doc["lk"], _id=doc["_id"]) if doc.get("lk", None) is not None else None

        args["cart"] = \
            cart_module.Cart.document_repr_to_object(doc["crt"], _id=doc["_id"]) if doc.get("crt", None) is not None else cart_module.Cart(
                args["_id"], [])

        args["order_history"] \
            = order_history_module.OrderHistory.document_repr_to_object(doc["odh"], _id=doc["_id"]) if doc.get("odh",
                                                                                                               None) is not None else order_history_module.OrderHistory(
            args["_id"], [])

        if args.get("is_system_admin", None) is None:
            args["is_system_admin"] = False

        return cls(**args)

    @staticmethod
    def get_db_repr(user: User, get_long_names: bool = False):
        res = {value: getattr(user, key) for key, value in User.LONG_TO_SHORT.items()}

        res["pfp"] = res["pfp"].image_id
        res["op"] = user_options.UserOptions.get_db_repr(user.options, get_long_names)
        res["sa"] = list(map(lambda address: shipping_address.ShippingAddress.get_db_repr(address, get_long_names), user.shipping_addresses))
        res["lk"] = liked_items_module.LikedItems.get_db_repr(user.liked_items, get_long_names)
        res["crt"] = cart_module.Cart.get_db_repr(user.cart, get_long_names) if user.cart is not None else []
        res["odh"] = order_history_module.OrderHistory.get_db_repr(user.order_history, get_long_names) if user.order_history is not None else []

        if get_long_names:
            res['_id'] = str(res['_id'])
            res = {user.lengthen_field_name(key): value for key, value in res.items()}

        return res

    @staticmethod
    def create_new_user(
            email=None,
            name=None,
            phone=None,
            password=None,
            hash_password=True
    ) -> User:
        default_user_repr = User.default_object_repr(email, name, phone, password, hash_password)
        return User.document_repr_to_object(
            users_collection.find_one_and_replace(
                {"_id": default_user_repr["_id"]},
                default_user_repr,
                upsert=True,
                return_document=ReturnDocument.AFTER
            ))

    @staticmethod
    def default_object_repr(
            email=None,
            name=None,
            phone=None,
            password=None,
            hash_password=True
    ) -> dict:
        return {
            "_id": ObjectId(),
            "ml": email,
            "nm": name,
            "ph": phone,
            "pw": User.hash_password(password) if hash_password else password,
            "pfp": None,
            "op": user_options.UserOptions.default_object_repr(),
            "sa": shipping_address.ShippingAddress.default_object_repr(),
            "lk": liked_items_module.LikedItems.default_object_repr(),
            "crt": [],
            "odh": []
        }

    def build_access_token(self, sign=False):
        """
        Builds a token based on the user object
        :param sign: if true returns the signed base64 token, otherwise, returns json
        :return: 
        """
        token = {
            "id": str(self._id),
            "name": self.name,
            "email": self.email,
            "phone": self.phone
        }

        if hasattr(self, "business_id"):
            token["business_id"] = str(self.business_id)

        return token if not sign else JwtSecurity.create_access_token(token, access_token_blacklist.expiration_time)

    @staticmethod
    def delete_by_id(_id: ObjectId) -> DeleteResult:
        UserAuth.delete_by_id(_id)
        return users_collection.delete_one({"_id": _id})

    @staticmethod
    def hash_password(password: str) -> bytes:
        salt = bcrypt.gensalt(13)
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed

    @staticmethod
    def compare_to_hash(password: str, hashed_password: bytes):
        return bcrypt.checkpw(password.encode(), hashed_password)

    def compare_hash(self, password: str):
        return User.compare_to_hash(password, self.password)

    def shorten_field_name(self, field_name):
        return User.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return User.SHORT_TO_LONG.get(field_name, None)

    @property
    def id(self):
        return self._id

    def __getstate__(self):
        res = User.get_db_repr(self, True)
        del res['password']
        del res['is_system_admin']
        return res

    def __setstate__(self, state):
        self.__dict__.update(state)
