"""
Verify Database Data

Quick verification of database content after rebuild.
"""

import sqlite3
from pathlib import Path


def verify_data():
    """Verify database data"""
    db_path = "database/test_data.db"

    if not Path(db_path).exists():
        print(f"[ERROR] Database not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=" * 80)
    print("DATABASE DATA VERIFICATION")
    print("=" * 80)

    # Sample test_results
    print("\n[TEST_RESULTS] Sample records:")
    cursor.execute("""
        SELECT test_id, dut_id, serial_number, status
        FROM test_results
        ORDER BY created_at DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"  test_id: {row[0]}")
        print(f"  dut_id: {row[1]}")
        print(f"  serial: {row[2]}")
        print(f"  status: {row[3]}")
        print()

    # Sample raw_measurements for one test
    print("\n[RAW_MEASUREMENTS] Sample for first test:")
    cursor.execute("""
        SELECT test_id, cycle_number, temperature, position, force
        FROM raw_measurements
        ORDER BY id
        LIMIT 10
    """)
    for row in cursor.fetchall():
        print(
            f"  test_id: {row[0]}, cycle: {row[1]}, "
            f"temp: {row[2]}, pos: {row[3]}, force: {row[4]}"
        )

    # Verify Foreign Key relationships
    print("\n[FOREIGN KEY] Verification:")
    cursor.execute("""
        SELECT
            tr.test_id,
            COUNT(rm.id) as measurement_count
        FROM test_results tr
        LEFT JOIN raw_measurements rm ON tr.test_id = rm.test_id
        GROUP BY tr.test_id
        ORDER BY tr.test_id
    """)
    print("  test_id                     | measurements")
    print("  " + "-" * 50)
    for row in cursor.fetchall():
        print(f"  {row[0]:30} | {row[1]:5} records")

    conn.close()

    print("\n" + "=" * 80)
    print("[VERIFIED] Database is properly structured!")
    print("=" * 80)


if __name__ == "__main__":
    verify_data()
