from sqlalchemy import create_engine, MetaData, Column, String
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Query
from sqlalchemy_utils import database_exists, create_database


class SQLAlchemyDatabase:
    def __init__(self, url: str):
        self.engine = None
        self.session = None

        self.url = url

        self._setup()

    def _commit(self):
        self.session.commit()

    def _close(self):
        self.session.close()

    def _setup(self):
        if not self.url:
            return

        self.engine = create_engine(url=self.url)

        if not self.engine:
            return

        if not database_exists(url=self.engine.url):
            create_database(url=self.engine.url)

        MetaData().create_all(bind=self.engine)

        _session = sessionmaker()
        _session.configure(bind=self.engine)
        self.session = _session()


class BaseDatabaseModel(DeclarativeBase):
    """
    Base class for all database models.
    Inherits from SQLAlchemy's Base class.
    """

    __abstract__ = True  # This class should not be instantiated directly


class Node(BaseDatabaseModel):
    __tablename__ = 'nodes'
    public_key = Column("public_key", String(255), primary_key=True,
                        nullable=False)  # Cannot have two nodes with the same public key
    name = Column("name", String(255), primary_key=True, nullable=False)


class Database(SQLAlchemyDatabase):
    def __init__(self, url: str):
        super().__init__(url=url)
        Node.__table__.create(bind=self.engine, checkfirst=True)

    def save_node(self, public_key: str, name: str) -> None:
        try:
            node_entry = Node(public_key=public_key, name=name)
            self.session.add(node_entry)
            self._commit()
        except Exception as e:
            print(f'Error saving node to database: {e}')
            self.session.rollback()

    def get_nodes_matching_partial_name(self, partial_name: str) -> list[Node]:
        query: Query = self.session.query(Node).filter(
            Node.name.like(f'%{partial_name}%')
        )
        return query.all()


def save_node_to_database(database: Database, public_key: str, name: str) -> None:
    database.save_node(public_key=public_key, name=name)


def get_nodes_matching_partial_name(database: Database, partial_name: str) -> list[Node]:
    """
    Get all nodes matching the provided partial name.
    :param database: The database to query.
    :type database: Database
    :param partial_name: The partial name to match against node names.
    :type partial_name: str
    :return: A list of Node objects matching the provided filters.
    :rtype: list[Node]
    """
    return database.get_nodes_matching_partial_name(partial_name=partial_name)
