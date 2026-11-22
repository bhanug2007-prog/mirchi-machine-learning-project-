"""Private farmer inventory and in-app target price alerts."""

import asyncio
from contextlib import contextmanager, suppress
from datetime import datetime, date, timedelta, timezone
import hashlib
import hmac
import logging
import os
from pathlib import Path
import secrets
import sqlite3
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator
from typing import Annotated


Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
IST = timezone(timedelta(hours=5, minutes=30))
SESSION_SECONDS = 12 * 60 * 60
QUOTE_MAX_AGE_DAYS = 3
bearer = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)


class Credentials(BaseModel):
    username: Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^[A-Za-z0-9_]{3,32}$")]
    password: str = Field(min_length=12, max_length=128)


class Lot(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)

    variety: Text
    market: Text = "Guntur APMC"
    location: Text
    quintals: float = Field(gt=0, le=100000)
    target_price: float = Field(gt=0, le=10000000)
    storage_type: Text
    stored_since: date
    storage_rate: float = Field(ge=0, le=100000)

    @field_validator("stored_since")
    @classmethod
    def validate_storage_date(cls, value):
        if value > datetime.now(IST).date():
            raise ValueError("Storage start cannot be in the future")
        return value


SCHEMA = (
    """CREATE TABLE IF NOT EXISTS portfolio_users (
        id TEXT PRIMARY KEY, username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS portfolio_sessions (
        token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES portfolio_users(id),
        expires_at BIGINT NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS portfolio_lots (
        id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES portfolio_users(id),
        variety TEXT NOT NULL, market TEXT NOT NULL, location TEXT NOT NULL,
        quintals DOUBLE PRECISION NOT NULL, target_price DOUBLE PRECISION NOT NULL,
        storage_type TEXT NOT NULL, stored_since TEXT NOT NULL, storage_rate DOUBLE PRECISION NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS portfolio_alerts (
        id TEXT PRIMARY KEY, lot_id TEXT NOT NULL REFERENCES portfolio_lots(id) ON DELETE CASCADE,
        quote_date TEXT NOT NULL, price DOUBLE PRECISION NOT NULL, target_price DOUBLE PRECISION NOT NULL,
        variety TEXT NOT NULL, market TEXT NOT NULL,
        UNIQUE (lot_id, market, variety, quote_date, target_price))""",
)


def password_digest(password, salt):
    return hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()


def hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()


def create_portfolio_router(quote_lookup, postgres_connect=None, sqlite_path=None):
    router = APIRouter(prefix="/api/portfolio", tags=["Farmer portfolio"])
    path = sqlite_path or os.getenv("PORTFOLIO_DB_PATH") or Path(__file__).with_name("portfolio.sqlite3")

    @contextmanager
    def transaction():
        conn = postgres_connect() if postgres_connect else sqlite3.connect(path, timeout=10)
        try:
            if not postgres_connect:
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA foreign_keys = ON")
            with conn:
                cursor = conn.cursor()

                def execute(sql, values=()):
                    cursor.execute(sql if postgres_connect else sql.replace("%s", "?"), values)
                    return cursor

                try:
                    yield execute
                finally:
                    cursor.close()
        finally:
            conn.close()

    def check_alerts(user_id=None):
        with transaction() as sql:
            if user_id is None:
                lots = sql("SELECT * FROM portfolio_lots").fetchall()
            else:
                lots = sql("SELECT * FROM portfolio_lots WHERE user_id = %s", (user_id,)).fetchall()
        today = datetime.now(IST).date()
        quotes = {}
        for row in lots:
            key = (row["market"], row["variety"])
            if key in quotes:
                continue
            try:
                quote = quote_lookup(*key)
                price = quote["modal_price"]
                quote_date = date.fromisoformat(quote["date"])
                if price is not None and price > 0 and quote_date <= today:
                    quotes[key] = (float(price), quote_date)
                    continue
            except HTTPException as error:
                if error.status_code != 404:
                    logger.warning("Portfolio market quote request failed with status %s", error.status_code)
            except Exception:
                logger.warning("Portfolio market quote unavailable")
            quotes[key] = (None, None)

        inventory = []
        with transaction() as sql:
            for row in lots:
                lot = dict(row)
                price, quote_date = quotes[(lot["market"], lot["variety"])]
                days = max(0, (today - date.fromisoformat(lot["stored_since"])).days)
                fresh = quote_date is not None and (today - quote_date).days <= QUOTE_MAX_AGE_DAYS
                if fresh and price >= lot["target_price"]:
                    sql("""INSERT INTO portfolio_alerts (id, lot_id, quote_date, price, target_price, variety, market)
                           SELECT %s, id, %s, %s, target_price, variety, market FROM portfolio_lots
                           WHERE id = %s AND target_price = %s AND market = %s AND variety = %s
                           ON CONFLICT (lot_id, market, variety, quote_date, target_price) DO NOTHING""",
                        (uuid4().hex, quote_date.isoformat(), price, lot["id"], lot["target_price"],
                         lot["market"], lot["variety"]))
                lot.pop("user_id")
                lot.update(quote_price=price, quote_date=quote_date, quote_fresh=fresh,
                           storage_days=days, storage_cost=round(days * lot["quintals"] * lot["storage_rate"], 2),
                           market_value=round(price * lot["quintals"], 2) if price is not None else None)
                inventory.append(lot)
        return inventory

    @router.on_event("startup")
    async def start_portfolio():
        router.alert_task = None
        try:
            with transaction() as sql:
                for statement in SCHEMA:
                    sql(statement)
        except Exception:
            logger.warning("Farmer portfolio storage could not be initialized")
            return
        try:
            interval = int(os.getenv("PORTFOLIO_ALERT_INTERVAL_SECONDS", "3600" if postgres_connect else "0"))
        except ValueError:
            logger.warning("Invalid PORTFOLIO_ALERT_INTERVAL_SECONDS; scheduled checks disabled")
            return
        if interval <= 0:
            return

        async def poll():
            while True:
                try:
                    await asyncio.to_thread(check_alerts)
                except Exception:
                    logger.warning("Farmer portfolio alert check failed; will retry")
                await asyncio.sleep(interval)

        router.alert_task = asyncio.create_task(poll())

    @router.on_event("shutdown")
    async def stop_portfolio():
        if router.alert_task:
            router.alert_task.cancel()
            with suppress(asyncio.CancelledError):
                await router.alert_task

    def authenticated(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
        if not credentials or len(credentials.credentials) != 43:
            raise HTTPException(401, "Sign in to access your portfolio")
        token_hash = hash_token(credentials.credentials)
        with transaction() as sql:
            row = sql("SELECT user_id FROM portfolio_sessions WHERE token_hash = %s AND expires_at > %s",
                      (token_hash, int(datetime.now(timezone.utc).timestamp()))).fetchone()
        if not row:
            raise HTTPException(401, "Session expired or invalid")
        return row["user_id"], token_hash

    @router.post("/register", status_code=201)
    def register(credentials: Credentials):
        salt = secrets.token_hex(16)
        stored = f"{salt}:{password_digest(credentials.password, salt)}"
        with transaction() as sql:
            result = sql("""INSERT INTO portfolio_users VALUES (%s, %s, %s)
                            ON CONFLICT (username) DO NOTHING""", (uuid4().hex, credentials.username.lower(), stored))
            if result.rowcount == 0:
                raise HTTPException(409, "Username is already taken")
        return {"registered": True}

    @router.post("/login")
    def login(credentials: Credentials, response: Response):
        now = int(datetime.now(timezone.utc).timestamp())
        with transaction() as sql:
            row = sql("SELECT id, password_hash FROM portfolio_users WHERE username = %s",
                      (credentials.username.lower(),)).fetchone()
        salt, expected = row["password_hash"].split(":", 1) if row else ("0" * 32, "0" * 64)
        valid = hmac.compare_digest(password_digest(credentials.password, salt), expected)
        if not row or not valid:
            raise HTTPException(401, "Invalid username or password")
        token = secrets.token_urlsafe(32)
        with transaction() as sql:
            sql("DELETE FROM portfolio_sessions WHERE expires_at <= %s", (now,))
            sql("INSERT INTO portfolio_sessions VALUES (%s, %s, %s)", (hash_token(token), row["id"], now + SESSION_SECONDS))
        response.headers["Cache-Control"] = "no-store"
        return {"token": token, "username": credentials.username.lower()}

    @router.post("/logout")
    def logout(account=Depends(authenticated)):
        with transaction() as sql:
            sql("DELETE FROM portfolio_sessions WHERE token_hash = %s", (account[1],))
        return {"signed_out": True}

    @router.get("")
    def dashboard(response: Response, account=Depends(authenticated)):
        lots = check_alerts(account[0])
        with transaction() as sql:
            alerts = sql("""SELECT a.id, a.quote_date, a.price, a.target_price, a.variety, a.market
                            FROM portfolio_alerts a JOIN portfolio_lots l ON a.lot_id = l.id
                            WHERE l.user_id = %s ORDER BY a.quote_date DESC, a.id LIMIT 30""", (account[0],)).fetchall()
        response.headers["Cache-Control"] = "no-store"
        return {"lots": lots, "alerts": [dict(row) for row in alerts]}

    @router.put("/lots/{lot_id}")
    def update_lot(lot_id: str, lot: Lot, account=Depends(authenticated)):
        with transaction() as sql:
            result = sql("""UPDATE portfolio_lots SET variety = %s, market = %s, location = %s, quintals = %s,
                            target_price = %s, storage_type = %s, stored_since = %s, storage_rate = %s
                            WHERE id = %s AND user_id = %s""", (*lot.model_dump(mode="json").values(), lot_id, account[0]))
            if result.rowcount == 0:
                raise HTTPException(404, "Inventory lot not found")
        return {"id": lot_id}

    @router.post("/lots", status_code=201)
    def create_lot(lot: Lot, account=Depends(authenticated)):
        lot_id = uuid4().hex
        with transaction() as sql:
            sql("INSERT INTO portfolio_lots VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (lot_id, account[0], *lot.model_dump(mode="json").values()))
        return {"id": lot_id}

    @router.delete("/lots/{lot_id}")
    def delete_lot(lot_id: str, account=Depends(authenticated)):
        with transaction() as sql:
            if sql("DELETE FROM portfolio_lots WHERE id = %s AND user_id = %s", (lot_id, account[0])).rowcount == 0:
                raise HTTPException(404, "Inventory lot not found")
        return {"deleted": True}

    return router
