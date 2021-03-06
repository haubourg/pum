import os
import shutil
from unittest import TestCase

import psycopg2
import psycopg2.extras

from core.dumper import Dumper


class TestDumper(TestCase):
    """Test the class Dumper.

    2 pg_services needed for test related to empty db:
        qwat_test_1
        qwat_test_2
    """

    def setUp(self):
        self.pg_service1 = 'qwat_test_1'
        self.pg_service2 = 'qwat_test_2'

        self.conn1 = psycopg2.connect("service={0}".format(self.pg_service1))
        self.cur1 = self.conn1.cursor()

        self.conn2 = psycopg2.connect("service={0}".format(self.pg_service2))
        self.cur2 = self.conn2.cursor()

        self.cur1.execute("""
            DROP SCHEMA IF EXISTS test_dumper CASCADE;
            CREATE SCHEMA test_dumper;
            CREATE TABLE test_dumper.dumper_table
                (
                id serial NOT NULL,
                version character varying(50),
                description character varying(200) NOT NULL,
                type integer NOT NULL
                );
            """)
        self.conn1.commit()

        self.cur2.execute("""
            DROP SCHEMA IF EXISTS test_dumper CASCADE;""")
        self.conn2.commit()

        try:
            shutil.rmtree('/tmp/test_dumper')
        except shutil.Error:
            pass

        os.mkdir('/tmp/test_dumper/')

    def test_dump_restore(self):
        dumper = Dumper(self.pg_service1, '/tmp/test_dumper/dump.sql')
        dumper.pg_backup()

        dumper = Dumper(self.pg_service2, '/tmp/test_dumper/dump.sql')
        dumper.pg_restore()

        # postgres > 9.4
        self.cur2.execute(
            "SELECT to_regclass('{}');".format('test_dumper.dumper_table'))
        self.assertIsNotNone(self.cur2.fetchone()[0])
