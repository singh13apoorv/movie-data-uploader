import os
from typing import Any, Dict, List, Optional

from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://singh13apoorv:XETTcALhmWfzBXIx@cluster0.qsk4j.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
MONGO_URI = os.getenv("MONGO_URI", uri)
DATABASE = os.getenv("DATABASE_NAME", "imdb_database")


class MongoConnect:
    """
    Summary: Connect with mongo with all required methods
    """

    def __init__(self):
        """
        Summary: Initialise the object.
        """
        self._CLIENT = MongoClient(MONGO_URI, server_api=ServerApi("1"))
        self._db = self._CLIENT[DATABASE]

        try:
            self._CLIENT.admin.command("ping")
            print("Pinged the deployment. You are successfully connected to MongoDB!")
        except Exception as e:
            print(f"Error occured: {e}")

    def get_collection(self, collection_name: str) -> Collection:
        """
        Summary: Get a collection.

        Args:
            collection_name (str): Name of the collection you want.
        Return:
            Collection: a mongo collection.
        """

        return self._db[collection_name]

    def insert_document(self, collection_name: str, document: Dict[str, Any]) -> str:
        """
        Summary: Insert a document into the specified collection.

        Args:
            collection_name(str): name of the collection.
            document (Dict[str, Any]): BJSON file to be inserted.

        Return:
            str: string contianing insert id.
        """
        collection = self.get_collection(collection_name)
        result = collection.insert_one(document)
        return str(result.inserted_id)

    def find_document(
        self, collection_name: str, query: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Summary: Find a single document in the specified collection.

        Args:
            collection_name (str): name of the collection.
            query (Dict[str, Any]): query to get data.
        Return:
            Optional[Dict[str, Any]]: Returns dictionary of data.
        """
        collection = self.get_collection(collection_name)
        return collection.find_one(query)

    def find_documents(
        self,
        collection_name: str,
        query: Dict[str, Any] = {},
        sort: Optional[str] = None,
        skip: int = 0,
        limit: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Summary: Find multiple documents in the specified collection.

        Args:
            collection_name (str): name of the collection.
            query (Dict[str, Any]): query dictionary.
            sort (str): Order you want your data in.
            limit (int): The number of data you want.

        Return:
            List: returns list of quried data.
        """
        collection = self.get_collection(collection_name)
        cursor = collection.find(query).limit(limit)

        if skip > 0:
            cursor = cursor.skip(skip)
        if limit > 0:
            cursor = cursor.limit(limit)
        if sort:
            cursor = cursor.sort(sort)
        return list(cursor)

    def update_document(
        self, collection_name: str, query: Dict[str, Any], update_data: Dict[str, Any]
    ) -> int:
        """
        Summary: Update a document in the specified collection.

        Args:
            collection_name (str): name of the collection.
            query (Dict[str, Any]): query dictionary.
            update_data (Dict[str, Any]): the new data.
        Return:
            int: count of data modified.
        """

        collection = self.get_collection(collection_name)
        result = collection.update_one(query, {"$set": update_data})
        return result.modified_count

    def delete_document(self, collection_name: str, query: Dict[str, Any]) -> int:
        """
        Summary: Delete a document from the specified collection.

        Args:
            collection_name (str): Name of the collection.
            query (Dict[str, Any]): query dictionary that contains query to delete data.

        Return:
            int: count of data deleted.
        """
        collection = self.get_collection(collection_name)
        result = collection.delete_one(query)
        return result.deleted_count

    def close_connection(self):
        """
        Summary: Close the connection to MongoDB.
        """
        self._CLIENT.close()
