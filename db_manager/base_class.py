from .db_connector import DBConnector


class BaseClass:
    def __init__(self) -> None:
        db_connector = DBConnector()
        self._connection = db_connector.connection
        self._cursor = db_connector.cursor
        self._get_connection_to_class = db_connector.get_connection_to_class