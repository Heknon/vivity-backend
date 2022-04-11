import base64

from bson import ObjectId
from web_framework_v2 import RequestBody, HttpResponse, HttpStatus, QueryParameter

from api import auth_fail, app
from database import User, Business, unapproved_businesses_collection, s3Bucket
from security import BlacklistJwtTokenAuth


class AdminController:
    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail, check_blacklist=True)
    @app.get("/business/unapproved")
    def get_unapproved_businesses(
            user_raw: BlacklistJwtTokenAuth,
            res: HttpResponse,
            get_images: QueryParameter("get_images", bool)
    ):
        user: User = user_raw
        if not user.is_system_admin:
            res.status = HttpStatus.UNAUTHORIZED
            return

        get_images = get_images if get_images is not None and isinstance(get_images, bool) else False
        businesses = list(map(lambda x: Business.document_repr_to_object(x), unapproved_businesses_collection.find()))
        if get_images:
            image_id_business_map = {}
            image_keys = []
            for business in businesses:
                image_keys.append(business.owner_id_card.image_id)
                image_id_business_map[business.owner_id_card.image_id] = business

            for key, image in s3Bucket.fetch_all(*image_keys):
                image_id_business_map[key].owner_id_card = base64.b64encode(image).decode('utf-8')
        else:
            for business in businesses:
                business.owner_id_card = None

        return businesses

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail, check_blacklist=True)
    @app.post("/business/approve")
    def update_business_approval(
            user_raw: BlacklistJwtTokenAuth,
            body: RequestBody(),
            res: HttpResponse
    ):
        user: User = user_raw
        if not user.is_system_admin:
            res.status = HttpStatus.UNAUTHORIZED
            return {
                "error": "Must be admin"
            }

        approved = body.get('approved', None)
        note = body.get("note", None)
        business_id = body.get("business_id", None)
        if note is None or approved is None or business_id is None:
            return {
                'error': 'Must pass body field: "approved" and "note"'
            }

        if not isinstance(approved, bool):
            return {
                'error': 'body field "approved" must be a boolean'
            }

        business_id = ObjectId(business_id)

        if approved:
            return Business.approve_business(business_id, note)
        else:
            return Business.move_business_to_unapproved(business_id, note)
