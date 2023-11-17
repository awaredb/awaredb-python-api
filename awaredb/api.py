from pathlib import Path
from typing import Any, Dict, List, Union

import json
import requests


class AwareDB:
    """
    Python API to interact with AwareDB.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        db: str,
        token=None,
        user: str = None,
        password: str = None,
        host: str = None,
    ):
        """
        :param db: Name of the database to connect to
        :type db: str
        :param user: Username of the database to connect to
        :type user: str
        :param pass: Password of the database to connect to
        :type pass: str
        :param host: Host of the database to connect to
        :type host: str
        :param token: Token of the database to connect to
        :type token: str
        """
        self.host = host or "https://aware-db.com"
        self.db = db
        self.user = user
        self.password = password
        self.token = token

        # Check if token or user and pass are provided
        if not token and not (user and password):
            raise ValueError("Database token or username and password are required")

        # If token is not provided, get it from the server
        if not self.token:
            self.token = self._get_token(user=user, password=password)

        # Check if connection is valid
        if not self._check_connection():
            raise ValueError("Unable to connect to database")

    # -------------------------------------------------------------------------
    # Login and connection methods
    # -------------------------------------------------------------------------

    def _check_connection(self):
        """
        Check if token is valid and if database exists.
        """
        return self._request("check") == {"connected": True}

    def _get_token(self, user: str = None, password: str = None):
        """
        Get a token from the server with the provided username and password.
        """
        response = requests.post(
            f"{self.host}/rest/auth/token/login/",
            json={"username": user, "password": password},
            timeout=30,
        )
        return response.json().get("token")

    # -------------------------------------------------------------------------
    # Read database commands
    # -------------------------------------------------------------------------

    def get(
        self,
        path: str,
        states: List[str] = None,
    ) -> Any:
        """
        Returns the value of a specific path from nodes in the database

        :param path: Path to get from the database.
        :type path: str
        :param states: List of states from which data should be retrieved.
        :type states: List[str]
        :return: Value of the path
        :rtype: Any
        """
        data = {"path": path, "states": states or []}
        return self._request("get", data)

    def query(
        self,
        nodes: List[str] = None,
        conditions: List[str] = None,
        properties: List[str] = None,
        states: List[str] = None,
        show_abstract: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Returns a list of nodes based on the input.

        :param nodes: List of ids, uids and names from nodes to fetch. Defaults to all.
        :type nodes: List[str]
        :param conditions: A list of conditions that validates if node should be retrieved.
        :type conditions: List[str]
        :param properties: A list of properties that should be retrieve. Defaults to all.
        :type properties: List[str]
        :param states: List of states from which data should be retrieved.
        :type states: List[str]
        :param show_abstract: If abstract nodes should be retrieved. Defaults to False.
        :type show_abstract: bool
        :return: Value of the path
        :rtype: Dict[str, Any]
        """
        data = {
            "nodes": nodes or ["*"],
            "conditions": conditions or [],
            "properties": properties or [],
            "states": states or [],
            "show_abstract": show_abstract,
        }
        return self._request("query", data)

    def calculate(
        self,
        formula: Union[str, List[str]],
        states: List[str] = None,
    ) -> Union[Any, List[Any]]:
        """
        Calculates a formula on the database.

        If only one formula is passed, the response will result of the calculation.
        If multiple formulas are passed, the response will be a list of results.

        :param formula: Formula to calculate
        :type formula: Union[str, List[str]]
        :return: Value of the formula
        :rtype: Union[Dict[str, Any], List[Dict[str, Any]]]
        """
        data = {"formula": formula, states: states or []}
        return self._request("calculate", data)

    def what_if(
        self,
        changes: Dict[str, Any],
        states: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Returns the impacts of changes without saving them on database.

        :param changes: A dictionary where keys represents paths and values the new values.
        :type changes: Dict[str, Any]
        :param states: List of states from which data should be retrieved.
        :type states: List[str]
        :return: Dictionary with the impacts of the changes.
        :rtype: Dict[str, Any]
        """
        data = {"changes": changes, states: states or []}
        return self._request("what-if", data)

    # -------------------------------------------------------------------------
    # Write database commands
    # -------------------------------------------------------------------------

    def update(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        partial: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Updates nodes on the database.

        :param data: List of nodes, relations and relation types to created or update.
        :type data: List[Dict[str, Any]]
        :param partial: Updates only passed properties for exiting data. Defaults to False.
        :type partial: bool
        :return: List of updated nodes, relations and relation types.
        :rtype: List[Dict[str, Any]]
        """
        data = {"data": data, "partial": partial}
        return self._request("update", data)

    def remove(self, ids: List[str]) -> None:
        """
        Removes specific nodes, relations and relation types from database.

        :param ids: List of ids from nodes, relations and relation types to remove.
        :type ids: List[str]
        """
        data = {"ids": ids}
        return self._request("remove", data)

    def flush(self) -> None:
        """
        Removes all nodes, relations and relation types from database.
        """
        return self._request("flush")

    # -------------------------------------------------------------------------
    # Generic methods to handle command requests
    # -------------------------------------------------------------------------

    def _request(self, command: str, data: Dict[str, Any] = None) -> Any:
        """
        Run a command on the server

        :param command: Command to execute on the server.
        :type command: str
        :param data: Data to send to the server as part of the command.
        :type data: Dict[str, Any]
        :return: Servers response
        :rtype: Any
        """
        url = f"{self.host}/rest/db/{self.db}/{command}/"
        response = requests.post(
            url,
            json=data or {},
            headers={"Authorization": f"Token {self.token}"},
            timeout=180,
        )
        if response.status_code == 400:
            raise ValueError("Invalid request", response.json())
        if response.status_code != 200:
            raise ValueError("Invalid request", response.content)
        return response.json().get("data")

    # -------------------------------------------------------------------------
    # Load and save database methods
    # -------------------------------------------------------------------------

    def load(self, filepath: str, recursive: bool = False, flush: bool = False):
        """
        Load a file or folder of JSONs into the database.
        """
        path = Path(filepath)

        # If path is invalid, theres nothing to load
        if not path.exists():
            raise ValueError(f"Path {path} does not exist.")

        # If flush is True, remove all data from database
        if flush:
            self.flush()

        # Gather data to be loaded
        data = []
        if path.is_dir():
            self._load_folder(data, path, recursive)
        else:
            self._load_file(data, path)

        # Upload data to database
        self.update(data)

    def _load_folder(
        self, data: List[Dict[str, Any]], path: Path, recursive: bool = False
    ):
        """
        Loads a folder of JSONs into list of data to be loaded.
        """
        for file in path.iterdir():
            if file.is_dir():
                if recursive:
                    self._load_folder(data, file, recursive=recursive)
            elif file.suffix.lower() == ".json":
                self._load_file(data, file)

    def _load_file(self, data: List[Dict[str, Any]], path: Path):
        """
        Loads a JSON file into a list of data to be loaded.
        """
        with open(path, "r", encoding="utf-8") as f:
            content = json.load(f)

        if isinstance(content, list):
            data.extend(content)
        else:
            data.append(content)
