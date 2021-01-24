#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import sys, os.path
import sqlite3
import string, base64

from .color import Color

class Database(object):
    dbName = "stats.db"

    def __init__(self, auto_create = True):
        if not os.path.isfile(self.dbName):
            if auto_create:
                self.createDB()
            else:
                raise Exception("Database not found")


    def insertUri(self, uri, result_code, result_length):
        try:
            conn = sqlite3.connect(self.dbName)
            cursor = conn.cursor()

            cursor.execute("""
            insert into [stats] ([uri], [result_code], [result_length])
            VALUES (?,?,?);
            """, (uri, result_code, result_length,))

            conn.commit()

            conn.close()

        except Exception as e:
            Color.pl('{!} {R}Error inserting data:{O} %s{W}' % str(e))
        pass


    def createDB(self):
        # conectando...
        conn = sqlite3.connect(self.dbName)
        # definindo um cursor
        cursor = conn.cursor()

        # criando a tabela (schema)
        cursor.execute("""
            CREATE TABLE [stats] (
                id_uri INTEGER PRIMARY KEY AUTOINCREMENT,
                uri TEXT NOT NULL, 
                result_code INTEGER NOT NULL DEFAULT(0),
                result_length INTEGER NOT NULL DEFAULT(0),
                created_date datetime not null DEFAULT (datetime('now','localtime'))
            );
        """)

        #print('DB criado com sucesso.')
        # desconectando...
        conn.close()
