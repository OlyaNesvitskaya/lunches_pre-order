from sqlalchemy import text

from settings import SessionLocal


def truncate_table(table: str) -> None:
    with SessionLocal() as session:
        statement = text(f'DELETE FROM {table}')
        session.execute(statement)
        session.commit()






