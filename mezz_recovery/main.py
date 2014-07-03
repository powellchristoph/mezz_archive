#!/usr/bin/env python

from bottle import route, run, template, static_file, post, request
from datetime import datetime
import multiprocessing
import os
import sqlite3
import subprocess
import time

ARCHIVE_ROOT = '/stornext/snfs1/VOD/Archive'

STATIC_ROOT = os.path.join(os.getcwd(), 'static')
DATABASE = 'mezz.db'

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=STATIC_ROOT)

@route('/mezz/')
def index():
    data = {}
    # Query database for previous recoverys and status
    conn = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("SELECT asset, status, submitted_time, start_time, completed_time FROM Transfers ORDER BY id DESC;")
    rows = c.fetchall()
    c.close()
    data['rows'] = rows

    # Scan providers
    providers = os.listdir(ARCHIVE_ROOT)
    providers.sort()
    data['providers'] = providers

    return template('index', data=data)

@route('/mezz/<provider>/')
def show_assets(provider):
    data = {}
    assets = os.listdir(os.path.join(ARCHIVE_ROOT, provider))
    assets.sort()

    data['provider'] = provider
    data['assets'] = assets

    return template('show_asset', data=data)

@post('/mezz/get/')
def get_assets():
    provider = request.forms.get('provider')
    assets = request.forms.getall('assets')

    conn = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    for a in assets:
        f = os.path.join(provider, a)
        c.execute("INSERT INTO Transfers(asset,status,submitted_time) VALUES (?,'Pending',?);", (f, datetime.now()))
    conn.commit()
    c.close()

    data = {}
    data['provider'] = provider
    data['assets'] = assets
    return template('confirm', data=data)

if __name__ == "__main__":

    run(host='IP_HERE', port=8080, reloader=True)
