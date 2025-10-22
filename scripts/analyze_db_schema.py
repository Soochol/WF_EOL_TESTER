"""
Database Schema Analysis Script

Analyzes the current database schema and provides recommendations.
"""

import sqlite3
from pathlib import Path


def analyze_schema(db_path: str):
    """Analyze database schema and relationships"""

    db_file = Path(db_path)
    if not db_file.exists():
        print(f"[ERROR] Database not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=" * 80)
    print("DATABASE SCHEMA ANALYSIS")
    print("=" * 80)

    # 1. Analyze test_results table
    print("\n[TABLE] test_results")
    print("-" * 80)

    cursor.execute("PRAGMA table_info(test_results)")
    columns = cursor.fetchall()
    print("\n[COLUMNS]")
    for col in columns:
        print(f"  {col[1]:20} {col[2]:15} {'PK' if col[5] else ''} {'NOT NULL' if col[3] else 'NULL'}")

    cursor.execute("PRAGMA index_list(test_results)")
    indexes = cursor.fetchall()
    print("\n[INDEXES]")
    for idx in indexes:
        print(f"  {idx[1]:30} Unique: {idx[2]}")
        cursor.execute(f"PRAGMA index_info({idx[1]})")
        cols = cursor.fetchall()
        for col in cols:
            print(f"    - Column: {col[2]}")

    cursor.execute("PRAGMA foreign_key_list(test_results)")
    fks = cursor.fetchall()
    print("\n[FOREIGN KEYS]")
    if fks:
        for fk in fks:
            print(f"  {fk}")
    else:
        print("  None")

    cursor.execute("SELECT COUNT(*) FROM test_results")
    count = cursor.fetchone()[0]
    print(f"\n[DATA] Total records: {count}")

    # 2. Analyze raw_measurements table
    print("\n" + "=" * 80)
    print("[TABLE] raw_measurements")
    print("-" * 80)

    cursor.execute("PRAGMA table_info(raw_measurements)")
    columns = cursor.fetchall()
    print("\n[COLUMNS]")
    for col in columns:
        print(f"  {col[1]:20} {col[2]:15} {'PK' if col[5] else ''} {'NOT NULL' if col[3] else 'NULL'}")

    cursor.execute("PRAGMA index_list(raw_measurements)")
    indexes = cursor.fetchall()
    print("\n[INDEXES]")
    for idx in indexes:
        print(f"  {idx[1]:30} Unique: {idx[2]}")
        cursor.execute(f"PRAGMA index_info({idx[1]})")
        cols = cursor.fetchall()
        for col in cols:
            print(f"    - Column: {col[2]}")

    cursor.execute("PRAGMA foreign_key_list(raw_measurements)")
    fks = cursor.fetchall()
    print("\n[FOREIGN KEYS]")
    if fks:
        for fk in fks:
            print(f"  Column: {fk[3]} -> {fk[2]}.{fk[4]} ON DELETE {fk[6]}")
    else:
        print("  None")

    cursor.execute("SELECT COUNT(*) FROM raw_measurements")
    count = cursor.fetchone()[0]
    print(f"\n[DATA] Total records: {count}")

    # 3. Check referential integrity
    print("\n" + "=" * 80)
    print("[REFERENTIAL INTEGRITY CHECK]")
    print("-" * 80)

    # Check orphaned raw_measurements (test_id not in test_results)
    cursor.execute("""
        SELECT DISTINCT rm.test_id, COUNT(*) as count
        FROM raw_measurements rm
        LEFT JOIN test_results tr ON rm.test_id = tr.test_id
        WHERE tr.test_id IS NULL
        GROUP BY rm.test_id
    """)
    orphans = cursor.fetchall()

    if orphans:
        print("\n[WARNING] Orphaned raw_measurements (no matching test_results):")
        for orphan in orphans:
            print(f"  test_id: {orphan[0]}, count: {orphan[1]}")
    else:
        print("\n[OK] No orphaned raw_measurements found")

    # Check test_results without raw_measurements
    cursor.execute("""
        SELECT tr.test_id, tr.serial_number, tr.status
        FROM test_results tr
        LEFT JOIN raw_measurements rm ON tr.test_id = rm.test_id
        WHERE rm.test_id IS NULL
    """)
    no_measurements = cursor.fetchall()

    if no_measurements:
        print("\n[INFO] test_results without raw_measurements:")
        for test in no_measurements:
            print(f"  test_id: {test[0]}, serial: {test[1]}, status: {test[2]}")
    else:
        print("\n[OK] All test_results have raw_measurements")

    # 4. Check foreign key settings
    print("\n" + "=" * 80)
    print("[FOREIGN KEY SETTINGS]")
    print("-" * 80)

    cursor.execute("PRAGMA foreign_keys")
    fk_enabled = cursor.fetchone()[0]
    print(f"\nForeign Keys Enabled: {'YES' if fk_enabled else 'NO (WARNING!)'}")

    conn.close()

    print("\n" + "=" * 80)
    print("[ANALYSIS COMPLETE]")
    print("=" * 80)


if __name__ == "__main__":
    analyze_schema("database/test_data.db")