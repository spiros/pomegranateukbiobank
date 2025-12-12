#!/usr/bin/env python
""" Script to check if we are connected to the database. """

from pomegranate.db.ukbdb import UKBDatabase

try:
    DatabaseConnection = UKBDatabase()
    print('✅')
except Exception as e:
    print('😞')
