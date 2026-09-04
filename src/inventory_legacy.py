# Legacy inventory module - deliberately dated style, no tests, no docs.
# Demo target for: explain, refactor, document, modernize, generate tests, find edge cases.

import sqlite3

DB = "inventory.db"

def get_stock(conn, sku):
    c = conn.cursor()
    c.execute("SELECT qty FROM stock WHERE sku = '" + sku + "'")
    r = c.fetchone()
    if r == None:
        return 0
    return r[0]

def adjust(conn, sku, delta):
    q = get_stock(conn, sku)
    n = q + delta
    if n < 0:
        n = 0
    c = conn.cursor()
    c.execute("UPDATE stock SET qty = %d WHERE sku = '%s'" % (n, sku))
    conn.commit()
    return n

def reorder_report(conn, threshold):
    c = conn.cursor()
    c.execute("SELECT sku, qty, reorder_point FROM stock")
    out = []
    for row in c.fetchall():
        sku = row[0]
        qty = row[1]
        rp = row[2]
        if qty < rp and qty < threshold:
            out.append(sku + ": " + str(qty) + " below " + str(rp))
    return out

def price_with_tax(price, rate):
    return price * (1 + rate)

def bulk_import(conn, rows):
    for r in rows:
        c = conn.cursor()
        c.execute("INSERT INTO stock VALUES ('%s', %d, %d)" % (r[0], r[1], r[2]))
    conn.commit()
