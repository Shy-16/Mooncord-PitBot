
## Database Module ##
# Connect to database and prepare a connection. #

import logging
from typing import List, Optional, Tuple

from datetime import datetime
from bson.objectid import ObjectId

log: logging.Logger = logging.getLogger("database")


class StickerDatabase:

    def __init__(self, *, database):
        self._db = database._db

    def close(self):
        self._db.close()

    # Timeouts
    def get_sticker(self, query: dict) -> Optional[dict]:
        """
        Return information about a single sticker.

        In the case of being multiple it will always return the first.
        """
        col = self._db['sticker_stats']
        if query.get("_id"):
            query['_id'] = ObjectId(query['_id'])
        result = col.find_one(query)
        return result

    def get_stickers(self, query: dict, sort: Optional[Tuple[str, int]] = None) -> List[dict]:
        """Return information about sticker(s)"""
        col = self._db['sticker_stats']
        if query.get("_id"): 
            query['_id'] = ObjectId(query['_id'])
        results = col.find(query)
        if sort:
            results = results.sort(sort[0], sort[1])
        results = list(results)
        return results

    def create_sticker(self, sticker: dict, channel_id: Optional[str]) -> dict:
        """Create a new sticker in the database."""

        col = self._db['sticker_stats']

        db_sticker = col.find_one({'id': str(sticker.id)})

        if db_sticker is None:
            db_sticker = {
                'id': str(sticker.id),
                'name': sticker.name,
                'format_type': sticker.format,
                'channels': {
                    channel_id: 1
                },
                'created_date': datetime.now().isoformat(),
                'updated_date': datetime.now().isoformat()
            }

            result = col.insert_one(db_sticker)
            db_sticker['_id'] = result.inserted_id

        return db_sticker

    def update_sticker(self, *, params: dict, query: dict = None, sticker_id: str = None) -> Optional[dict]:
        """Update a sticker from database."""

        col = self._db['sticker_stats']

        if query is None and sticker_id is None:
            raise Exception("query and sticker_id cannot be None")

        if query is None:
            query = dict()

        if sticker_id is not None:
            query['id'] = sticker_id

        if query.get("_id"): query['_id'] = ObjectId(query['_id'])
        if params.get("_id"): params['_id'] = ObjectId(params['_id'])
        params['updated_date'] = datetime.now().isoformat()

        result = col.find_one_and_update(query, {"$set" : params })

        return result

    def update_sticker_stats(self, *, sticker: dict, channel_id: str) -> Optional[dict]:
        """
        Given a sticker_id update the stat of the given channel_id
        """

        col = self._db['sticker_stats']

        if channel_id in sticker['channels']:
            updated_info = col.find_one_and_update(
                {'id': str(sticker.id)}, 
                {"$set": 
                    {f'channels.{channel_id}': sticker['channels'][channel_id]+1,
                    'updated_date': datetime.now().isoformat()}
                })

        else:
            updated_info = col.find_one_and_update(
                {'id': str(sticker.id)}, 
                {"$set": 
                    {f'channels.{channel_id}': 1,
                    'updated_date': datetime.now().isoformat()}
                })

        return updated_info
