"""
Delete test data from database

This script deletes records from test_results and raw_measurements tables.
"""

import sqlite3
from pathlib import Path


def delete_test_results(db_path: str, start_id: int = 9):
    """
    Delete test results from database starting from specified ID

    Args:
        db_path: Path to SQLite database file
        start_id: Starting ID to delete from (inclusive)
    """
    db_file = Path(db_path)

    if not db_file.exists():
        print(f"[ERROR] Database file not found: {db_path}")
        return

    print(f"[INFO] Database: {db_path}")
    print(f"[INFO] Deleting test_results with ID >= {start_id}")

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Count records to be deleted
        cursor.execute("SELECT COUNT(*) FROM test_results WHERE id >= ?", (start_id,))
        count_to_delete = cursor.fetchone()[0]

        # Get total count before deletion
        cursor.execute("SELECT COUNT(*) FROM test_results")
        total_before = cursor.fetchone()[0]

        print(f"[INFO] Total test_results before: {total_before}")
        print(f"[INFO] Records to delete: {count_to_delete}")

        if count_to_delete == 0:
            print("[INFO] No records to delete from test_results")
            return

        # Get sample of records to be deleted
        cursor.execute(
            "SELECT id, test_id, dut_id, serial_number, status FROM test_results "
            "WHERE id >= ? ORDER BY id LIMIT 5",
            (start_id,)
        )
        samples = cursor.fetchall()

        print("\n[SAMPLE] Records to be deleted from test_results:")
        for record in samples:
            print(f"  ID: {record[0]}, test_id: {record[1]}, dut_id: {record[2]}, "
                  f"serial: {record[3]}, status: {record[4]}")

        # Delete records (CASCADE will delete related raw_measurements)
        cursor.execute("DELETE FROM test_results WHERE id >= ?", (start_id,))
        deleted_count = cursor.rowcount
        conn.commit()

        # Get total count after deletion
        cursor.execute("SELECT COUNT(*) FROM test_results")
        total_after = cursor.fetchone()[0]

        print(f"\n[SUCCESS] test_results deletion complete!")
        print(f"[INFO] Total records after: {total_after}")
        print(f"[INFO] Records deleted: {deleted_count}")

    except Exception as e:
        print(f"[ERROR] Error during deletion: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_raw_measurements(db_path: str, start_id: int = 129):
    """
    Delete raw measurements from database starting from specified ID

    Args:
        db_path: Path to SQLite database file
        start_id: Starting ID to delete from (inclusive)
    """
    db_file = Path(db_path)

    if not db_file.exists():
        print(f"[ERROR] Database file not found: {db_path}")
        return

    print(f"\n[INFO] Database: {db_path}")
    print(f"[INFO] Deleting raw_measurements with ID >= {start_id}")

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Count records to be deleted
        cursor.execute("SELECT COUNT(*) FROM raw_measurements WHERE id >= ?", (start_id,))
        count_to_delete = cursor.fetchone()[0]

        # Get total count before deletion
        cursor.execute("SELECT COUNT(*) FROM raw_measurements")
        total_before = cursor.fetchone()[0]

        print(f"[INFO] Total raw_measurements before: {total_before}")
        print(f"[INFO] Records to delete: {count_to_delete}")

        if count_to_delete == 0:
            print("[INFO] No records to delete from raw_measurements")
            return

        # Get sample of records to be deleted
        cursor.execute(
            "SELECT id, test_id, serial_number, timestamp FROM raw_measurements "
            "WHERE id >= ? ORDER BY id LIMIT 5",
            (start_id,)
        )
        samples = cursor.fetchall()

        print("\n[SAMPLE] Records to be deleted from raw_measurements:")
        for record in samples:
            print(f"  ID: {record[0]}, test_id: {record[1]}, serial: {record[2]}, time: {record[3]}")

        # Delete records
        cursor.execute("DELETE FROM raw_measurements WHERE id >= ?", (start_id,))
        deleted_count = cursor.rowcount
        conn.commit()

        # Get total count after deletion
        cursor.execute("SELECT COUNT(*) FROM raw_measurements")
        total_after = cursor.fetchone()[0]

        print(f"\n[SUCCESS] raw_measurements deletion complete!")
        print(f"[INFO] Total records after: {total_after}")
        print(f"[INFO] Records deleted: {deleted_count}")

    except Exception as e:
        print(f"[ERROR] Error during deletion: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    # Database path
    db_path = "database/test_data.db"

    print("=" * 70)
    print("Database Cleanup Script")
    print("=" * 70)

    # Delete from test_results (ID >= 9)
    print("\n[STEP 1] Deleting test_results (ID >= 9)")
    delete_test_results(db_path, start_id=9)

    # Delete from raw_measurements (ID >= 129)
    print("\n[STEP 2] Deleting raw_measurements (ID >= 129)")
    delete_raw_measurements(db_path, start_id=129)

    print("\n" + "=" * 70)
    print("[DONE] Database cleanup complete!")
    print("=" * 70)
