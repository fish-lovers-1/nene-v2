from db.Base import Base


def get_all_db_tables() -> list[type[Base]]:
    return [mapper.class_ for mapper in Base.registry.mappers]
