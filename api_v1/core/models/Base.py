from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr


class MegaBase(DeclarativeBase):
    __abstract__ = True


class Base(MegaBase):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'

    id: Mapped[int] = mapped_column(primary_key=True)


class AuthBase(MegaBase):
    __abstract__ = True
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'