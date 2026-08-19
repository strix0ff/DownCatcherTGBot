from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker
)

from sqlalchemy.orm import ( 
    DeclarativeBase, 
    Mapped, 
    mapped_column
)

from sqlalchemy import (
    select,
    delete
)

from api.config import (
    DBNAME
)

class Base(DeclarativeBase):
    pass

class Service(Base):
    __tablename__ = 'services'
    id: Mapped[str] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()

engine = create_async_engine(url=f'sqlite+aiosqlite:///{DBNAME}.db')
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def db_add(id: str, address: str, name: str):
    async with async_session() as session:
        Newservice = Service(id=id, address=address, name=name)
        session.add(Newservice)
        await session.commit()

async def db_remove(id: str) -> bool | None:
    async with async_session() as session:
        stmt = select(Service).where(Service.id == id)
        result = await session.execute(stmt)
        found = result.scalar_one_or_none()
        if found is None:
            return None
        else:
            stmt = delete(Service).where(Service.id == id)
            result = await session.execute(stmt)
            await session.commit()
            return True

async def db_getall() -> dict:
    async with async_session() as session:
        stmt = select(Service)
        result = await session.execute(stmt)
        services = result.scalars().all()
        sort_dict = {}
        for service in services:
            sort_dict[service.id] = {'address': service.address, 'name': service.name}
        return sort_dict