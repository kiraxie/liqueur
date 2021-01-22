from . import SchemaBase, Config, Database, gen_uuid, Column, DateTime, Integer, Transaction, String
from datetime import datetime
from time import sleep
import unittest

from sqlalchemy.pool import StaticPool


class TestItem(SchemaBase):
    __tablename__ = 'test_items'
    id: Column = Column(String, nullable=False, primary_key=True)
    value: Column = Column(Integer, nullable=False)
    created_at: Column = Column(DateTime, nullable=False, primary_key=True)

    def __init__(self, v: int):
        self.id = gen_uuid().hex
        self.value = v
        self.created_at = datetime.now()

    def __repr__(self):
        return "test_items('{}','{}', '{}')".format(self.id, self.value, self.created_at)


class TestDAtabase(unittest.TestCase):
    def setUp(self):
        conf: Config = Config()
        self.db: Database = Database(
            'sqlite://', SchemaBase, connect_args={'check_same_thread': False},
            poolclass=StaticPool)
        self.db.start()

    def tearDown(self) -> None:
        self.db.stop()
        self.db.join()

    def test_create(self):
        tx: Transaction = self.db.transaction()
        v: TestItem = TestItem(123)

        tx.create(v)
        e = tx.query(TestItem).filter_by(value=123).first()
        self.assertEqual(v, e)

    def test_create_or_ignore(self):
        tx: Transaction = self.db.transaction()
        v: TestItem = TestItem(5566)

        self.assertTrue(tx.create_or_ignore(v))
        self.assertFalse(tx.create_or_ignore(v, id=v.id))

    def test_async(self):
        v1: TestItem = TestItem(1)
        v2: TestItem = TestItem(2)
        v3: TestItem = TestItem(3)

        self.db.async_create(v1)
        self.db.async_create_or_ignore(v1, id=v1.id)
        self.db.async_create_or_ignore(v2, id=v2.id)
        self.db.async_create_or_ignore(v3, id=v3.id)

        while not self.db._queue.empty():
            sleep(1)
        tx: Transaction = self.db.transaction()
        self.assertFalse(tx.create_or_ignore(v1, id=v1.id))


if __name__ == '__main__':
    unittest.main()
