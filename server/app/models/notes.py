import datetime
from app.db.sqlalchemy import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, func


class Note(Base):
    __tablename__ = "notes"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(String(255))
    create_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now()
    )
    update_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now()
    )