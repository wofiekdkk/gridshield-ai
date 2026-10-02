"""
Database Session Management with Built-in Dual-Mode Record Engine
"""
import sys
import types
import os
import json
from datetime import datetime
from app.core.logger import logger

# ---------------------------------------------------------
# Dynamic SQLAlchemy Module Registration (for offline env)
# ---------------------------------------------------------
class ColumnDef:
    def __init__(self, *args, **kwargs):
        self.name = None
        self.primary_key = kwargs.get("primary_key", False)
        self.default = kwargs.get("default", None)

    def __eq__(self, other):
        return ("eq", self.name or "id", other)

    def __ne__(self, other):
        return ("ne", self.name or "id", other)

    def in_(self, items):
        return ("in", self.name or "id", items)

    def desc(self):
        return ("desc", self.name or "id")

    def asc(self):
        return ("asc", self.name or "id")

    def label(self, name):
        return self

class FuncFactory:
    def count(self, col=None):
        return ("count", getattr(col, "name", "id"))
    def avg(self, col=None):
        return ("avg", getattr(col, "name", "id"))
    def sum(self, col=None):
        return ("sum", getattr(col, "name", "id"))

sqla = types.ModuleType("sqlalchemy")
sqla_orm = types.ModuleType("sqlalchemy.orm")
sqla.Column = ColumnDef
sqla.Integer = lambda *a, **kw: "Integer"
sqla.String = lambda *a, **kw: "String"
sqla.Float = lambda *a, **kw: "Float"
sqla.DateTime = lambda *a, **kw: "DateTime"
sqla.Boolean = lambda *a, **kw: "Boolean"
sqla.JSON = lambda *a, **kw: "JSON"
sqla.Text = lambda *a, **kw: "Text"
sqla.Enum = lambda *a, **kw: "Enum"
sqla.ForeignKey = lambda *a, **kw: "ForeignKey"
sqla.func = FuncFactory()
sqla_orm.declarative_base = lambda: object
sqla_orm.relationship = lambda *a, **kw: None
sqla_orm.Session = object

sys.modules["sqlalchemy"] = sqla
sys.modules["sqlalchemy.orm"] = sqla_orm

# ---------------------------------------------------------
# Universal Record Object
# ---------------------------------------------------------
class Record(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for k, v in kwargs.items():
            self[k] = v

    def __getattr__(self, name):
        if name in self:
            return self[name]
        return None

    def __setattr__(self, name, value):
        self[name] = value

# ---------------------------------------------------------
# Local In-Memory & File Store
# ---------------------------------------------------------
MOCK_DB_PATH = "D:/gridshield-ai/backend/gridshield_store.json"

class MemoryStore:
    def __init__(self):
        self.tables = {
            "users": [],
            "grid_components": [],
            "sensors": [],
            "sensor_readings": [],
            "fault_events": [],
            "ai_predictions": [],
            "fault_localizations": [],
            "recovery_plans": [],
            "recovery_actions": [],
            "grid_states": [],
            "system_events": [],
            "audit_logs": []
        }
        self.load()

    def load(self):
        if os.path.exists(MOCK_DB_PATH):
            try:
                with open(MOCK_DB_PATH, "r") as f:
                    data = json.load(f)
                    for table, records in data.items():
                        self.tables[table] = [Record(**r) for r in records]
                logger.info("Loaded store from disk.")
            except Exception as e:
                logger.error(f"Store read error: {e}")

    def save(self):
        try:
            os.makedirs(os.path.dirname(MOCK_DB_PATH), exist_ok=True)
            serializable = {}
            for table, records in self.tables.items():
                serializable[table] = [dict(r) for r in records]
            with open(MOCK_DB_PATH, "w") as f:
                json.dump(serializable, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Store write error: {e}")

store = MemoryStore()

# ---------------------------------------------------------
# Query & Session Interfaces
# ---------------------------------------------------------
class Query:
    def __init__(self, table_name):
        self.table_name = table_name
        self.items = list(store.tables.get(table_name, []))
        self._limit = None

    def filter(self, *conditions):
        for cond in conditions:
            if isinstance(cond, tuple):
                op, col, val = cond
                if op == "eq":
                    self.items = [r for r in self.items if r.get(col) == val]
                elif op == "ne":
                    self.items = [r for r in self.items if r.get(col) != val]
                elif op == "in":
                    self.items = [r for r in self.items if r.get(col) in val]
            elif callable(cond):
                self.items = [r for r in self.items if cond(r)]
        return self

    def order_by(self, *args):
        return self

    def limit(self, n):
        self._limit = n
        return self

    def all(self):
        return self.items[:self._limit] if self._limit else self.items

    def first(self):
        return self.items[0] if self.items else None

    def scalar(self):
        return len(self.items)

class Session:
    def __init__(self):
        self.new_items = []

    def query(self, model, *args):
        tname = getattr(model, "__tablename__", "generic")
        return Query(tname)

    def add(self, item):
        self.new_items.append(item)

    def commit(self):
        for item in self.new_items:
            rec = item if isinstance(item, Record) else Record(**item.__dict__)
            tname = rec.get("__tablename__", "generic")
            tbl = store.tables.setdefault(tname, [])
            
            if not rec.get("id"):
                rec.id = len(tbl) + 1

            # Match unique keys
            idx = -1
            if rec.get("username"):
                idx = next((i for i, x in enumerate(tbl) if x.get("username") == rec.username), -1)
            elif rec.get("fault_id"):
                idx = next((i for i, x in enumerate(tbl) if x.get("fault_id") == rec.fault_id), -1)
            elif rec.get("plan_id"):
                idx = next((i for i, x in enumerate(tbl) if x.get("plan_id") == rec.plan_id), -1)

            if idx != -1:
                tbl[idx] = rec
            else:
                tbl.append(rec)

        self.new_items.clear()
        store.save()

    def refresh(self, item):
        pass

    def close(self):
        pass

SessionLocal = Session
Base = object

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    logger.info("Universal In-Memory Database ready.")
