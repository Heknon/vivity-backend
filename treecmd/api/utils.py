import base64

from database import Item, s3Bucket


def applyImagesToItems(*items: Item):
    image_ids = []
    for item in items:
        for image in item.images:
            image_ids.append(image.image_id)

    images = {}
    for key, image in s3Bucket.fetch_all(*image_ids):
        images[key] = image

    for item in items:
        sorted_images = []
        for image_key in item.images:
            res = images.get(str(image_key))
            sorted_images.append(base64.b64encode(res).decode('utf-8'))
        item.images = sorted_images

    return items
