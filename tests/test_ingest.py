import sqlite3
import pytest

DB_PATH = "orders.db"

def test_table_exists():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='order_events'")
    result = cursor.fetchone()
    conn.close()
    assert result is not None, "order_events table should exist"

def test_all_three_domains_present():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT domain FROM order_events")
    domains = {row[0] for row in cursor.fetchall()}
    conn.close()
    assert "order_capture" in domains
    assert "fulfilment" in domains
    assert "logistics" in domains

def test_no_null_order_ids():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM order_events WHERE order_id IS NULL")
    count = cursor.fetchone()[0]
    conn.close()
    assert count == 0, "No order_id should be null"

def test_no_null_timestamps():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM order_events WHERE timestamp IS NULL")
    count = cursor.fetchone()[0]
    conn.close()
    assert count == 0, "No timestamp should be null"

def test_minimum_event_count():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM order_events")
    count = cursor.fetchone()[0]
    conn.close()
    assert count >= 6, "Should have at least 6 events across 3 domains"