# -*- coding:utf-8 -*-
import json
import typing
import sqlite3
from time import strftime, localtime
from dataclasses import dataclass
import asyncio

DEFAULT_VERSION = 11.4514
DEFAULT_DBDIR = r"./db/events.db"
DEFAULT_LOGFOLDER_DIR = r"./log"


def _addstra(x: str):
    return f"\"{x}\""


@dataclass
class Counter:
    ...


class Logable:
    """This class provide log writing/reading method"""

    def __init__(self):
        ...

    def __info(self, objname: str, text: str) -> str:
        ...

    def __warning(self, objname: str, text: str) -> str:
        ...

    def __error(self, objname: str, text: str) -> str:
        ...

    def __fatal(self):
        ...

    def writelog(self, mode: str, objname: str, text: str):
        logscript = f"[{strftime('%H:%M:%S', localtime())}] "
        if hasattr(self, f'__{mode}'):
            logscript += f"{getattr(self, f'__{mode}')(objname, text)}"
        else:
            logscript += f"{self.__error('Logable', f'Cannot find log mode: {mode}!')}"

    def trigger(self):
        ...


class Dbloder(Logable):
    """A class which provide a general encapsulated sqlite3 database CRUD operation"""

    def __init__(self, _dir: str = DEFAULT_DBDIR):
        super().__init__()
        self.dbDir = _dir
        self.dbConnect = sqlite3.connect(self.dbDir)
        self.dbCur = self.dbConnect.cursor()

    def execute(self, sqlscript: str, isfetch: bool = False) -> list | None:
        """
        execute a given SQL statement which to to sqlite3 DB operation.
        Params: sqlscript: str, isfetch: bool
        """
        print(sqlscript)
        selected = None
        try:
            if not isfetch:
                self.dbCur.execute(sqlscript)
            else:
                selected = self.dbCur.execute(sqlscript).fetchall()
        except Exception as ex:
            if isinstance(ex, sqlite3.OperationalError):
                print(f"Invaild sqlite3 Operational with this traceback: {ex}")
            else:
                raise ex

        finally:
            self.dbConnect.commit()

        return selected

    @staticmethod
    def __position(position: dict) -> str | None:
        return f"{' and '.join([f'{k}={v if type(v) != str else _addstra(v)}' for k, v in position.items()])}"

    @staticmethod
    def __setvalues(values: dict) -> str | None:
        return f"{''.join([f'{k} = {v if type(v) != str else _addstra(v)}' for k, v in values.items()])}"

    @staticmethod
    def __selection(column: list[str]):
        return f"{','.join(map(str, column))}"

    @staticmethod
    def __creation(attributes: list[str] | tuple[str]):
        return f"{' '.join(attributes)}"

    def __selected_tuple_to_dict(self, tablename: str, selected: list[tuple]) -> list[dict]:
        schema = list(self.schema(tablename).keys())
        formated: list[dict] = []
        for i in selected:
            formated.append({schema[j]: v for j, v in enumerate(i)})

        return formated

    def schema(self, tablename: str) -> dict | None:
        """
        Return a table's schema by given tablename in forms of {column: type, ...}
        params: tablename: str
        """
        selected = self.execute(f"PRAGMA table_info({tablename});", isfetch=True)
        return {_[1]: _[2] for _ in selected} if selected else None

    def create(self, name: str, attribute: dict[str:list[str]] | tuple[str]):
        """
        Create a SQL statement which to create a table.
        Params: tablename: str, attribute: {column: [type,attributes,...], ...}
        """
        sqlscript = f"CREATE TABLE {name}(\n" + \
                    "".join((f"\t{k} {self.__creation(v)},\n" for k, v in attribute.items()))[:-2] + "\n)"
        self.execute(sqlscript)

        return sqlscript

    def select(self, tablename: str, where: dict = None, columname: list[str] | str = None, limit: int | None = None,
               withcolumn: bool = 0) -> tuple | dict | None:
        """
        Create a SQL statement which to select data from table.
        Params: tablename: str, where: {"column": condition, ...}, columname: ["column", ...], limit: int, withcolumn: bool
        """
        sqlscript = f"SELECT {f'{self.__selection(columname)}' if type(columname) == list else '*'} FROM {tablename}" + \
                    f"{f' WHERE {self.__position(where)}' if where else ''} {f'LIMIT {limit}' if limit else ''}"
        selected = self.execute(sqlscript, isfetch=True)

        return tuple([sqlscript, (
            selected if not withcolumn and not selected else self.__selected_tuple_to_dict(tablename, selected))])

    def insert(self, tablename: str, values: dict = None):
        """
        Create a SQL statement which to insert a record to a table.
        Params: tablename: str, values: {"column": value, ...}
        """
        sqlscript = f"INSERT INTO {tablename} {tuple(values.keys())} VALUES {tuple(values.values())}"
        self.execute(sqlscript)

        return sqlscript

    def delete(self, tablename: str, where: dict = None):
        """
        Create a SQL statement which to delete records from a table.
        Params: tablename: str, where: {"column": condition}
        """
        sqlscript = f"DELETE from {tablename} WHERE {self.__position(where) if where else None}"
        self.execute(sqlscript)

        return sqlscript

    def update(self, tablename: str, values: dict = None, where: dict = None):
        """
        Create a SQL statement which to change record values from a table.
        Params: tablename: str,values: {"column": value} ,where: {"column": condition}
        """
        sqlscript = f"UPDATE {tablename} SET {self.__setvalues(values) if values else None} " + \
                    f"WHERE {self.__position(where) if where else None}"
        self.execute(sqlscript)

        return sqlscript

    def drop(self, tablename: str):
        """
        Create a SQL statement which to delete a table.
        Params: tablename: str
        """
        sqlscript = f"DROP TABLE {tablename}"
        self.execute(sqlscript)

        return sqlscript

    def __del__(self):
        self.dbConnect.commit()
        self.dbCur.close()
        self.dbConnect.close()


class Jsonloder(Logable):
    ...


class TodolistAPI(Logable, Counter):
    def __init__(self, version: int | float | str = DEFAULT_VERSION):
        super().__init__()
        self.version = version

    def getinfo(self, mode: int):
        return f"Todolist version:{(str, int, float)[mode](self.version)}"

    def __del__(self):
        return "Sccuessfull closed Todolist"


if __name__ == "__main__":
    todolist = TodolistAPI()
    dbloder = Dbloder()
    dbloder.select("events", where={"eventName": "D", "Id": 2})
    # write debugging code below
