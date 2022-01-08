from __future__ import annotations

import logging
import threading
import time

from pymongo import ReturnDocument

from database import blacklist_collection
from singleton import Singleton

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Blacklist(metaclass=Singleton):
    TOKEN_EXPIRATION_TIME = 60 * 30
    TOKEN_EXPIRATION_TIME_NS = TOKEN_EXPIRATION_TIME * (10 ** 9)

    def __init__(self):
        initial_document = self.get_blacklist_document()
        self._last_purge = initial_document["last_purge"]
        self._blacklist = set(initial_document["blacklist"].values())

        self._purge_thread = threading.Thread(name="Blacklist purger", target=lambda: self._purge_handler())

        self._purge_thread.start()
        logger.info("Initiated blacklist class and started blacklist purge thread.")
        logger.info(f"Blacklist data: {self._blacklist}")

    def add_to_blacklist(self, token: str):
        add_time = int(time.time_ns())

        blacklist_collection.update_one(
            {"_id": 1},
            {"$set": {f"blacklist.{add_time}": token}},
            upsert=True
        )

        self._blacklist.add(token)

    def remove_before_time(self, epoch_ms_time: int):
        doc = blacklist_collection.find_one_and_update(
            {"_id": 1},
            [{
                "$replaceWith": {
                    "last_purge": time.time_ns(),
                    "blacklist": {
                        "$arrayToObject": {
                            "$filter": {
                                "input": {"$objectToArray": "$$ROOT.blacklist"},
                                "cond": {
                                    "$gt": [
                                        {"$toLong": "$$this.k"},
                                        epoch_ms_time
                                    ]
                                }
                            }
                        }
                    }
                }
            }],
            return_document=ReturnDocument.AFTER
        )

        self._last_purge = doc["last_purge"]
        self._blacklist = set(doc["blacklist"].values())

    def _purge_handler(self):
        while True:
            wait_time = max(0, int(self.TOKEN_EXPIRATION_TIME - (time.time_ns() - self._last_purge) / (10 ** 9)))
            logger.debug(f"Time till next purge: {round(wait_time / 60.0, 3)}")
            time.sleep(wait_time)
            self.remove_before_time(self.get_time_expiration_time_ago())
            logger.debug("Purging blacklist!")

    def get_time_expiration_time_ago(self):
        curr = time.time_ns()
        return curr - self.TOKEN_EXPIRATION_TIME_NS

    def in_blacklist(self, token: str):
        return token in self._blacklist

    @staticmethod
    def get_blacklist_document():
        blacklist_doc = blacklist_collection.find_one({"_id": 1})

        if blacklist_doc is not None and "blacklist" in blacklist_doc:
            return blacklist_doc

        return blacklist_collection.find_one_and_update({"_id": 1}, {"$set": {"blacklist": dict(), "last_purge": time.time_ns()}}, upsert=True,
                                                        return_document=ReturnDocument.AFTER)
