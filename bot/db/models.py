from uuid import uuid4

from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy.dialects.postgresql import TIMESTAMP, TEXT, BIGINT, UUID, VARCHAR, BOOLEAN
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime

from db.base import Base


class utcnow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


user_notifications = Table(
    "user_notifications",
    Base.metadata,
    Column("bot_user_id", ForeignKey("bot_user.telegram_id"), primary_key=True),
    Column("notification_id", ForeignKey("notifications.notification_id"), primary_key=True),
)


class BotUser(Base):
    __tablename__ = "bot_user"

    telegram_id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True
    )
    registered_at: Mapped[int] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=utcnow()
    )
    login: Mapped[str] = mapped_column(
        VARCHAR,
        nullable=True
    )
    receive_notifications: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        server_default="false"
    )
    monitoring_runs_job: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        server_default="false"
    )
    notifications: Mapped[list["Notifications"]] = relationship(
        secondary=user_notifications,
        lazy="selectin"
    )


class Notifications(Base):
    __tablename__ = "notifications"

    notification_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    notification_name: Mapped[str] = mapped_column(
        TEXT,
        nullable=False
    )
    created_at: Mapped[int] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=utcnow()
    )
    bot_user: Mapped[list["BotUser"]] = relationship(
        secondary=user_notifications,
        lazy="selectin"
    )