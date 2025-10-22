"""
Cleanup Orphaned Records from Database

This script removes orphaned raw_measurements (measurements without matching test_results).
"""

import sqlite3
from pathlib import Path


def cleanup_orphaned_records(db_path: str):
    """
    Remove orphaned raw_measurements that don't have matching test_results

    Args:
        db_path: Path to SQLite database file
    """
    db_file = Path(db_path)
    if not db_file.exists():
        print(f"[ERROR] Database file not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("=" * 80)
        print("ORPHANED RECORDS CLEANUP")
        print("=" * 80)

        # Step 1: Find orphaned raw_measurements
        print("\n[STEP 1] Finding orphaned raw_measurements...")
        cursor.execute("""
            SELECT DISTINCT rm.test_id, COUNT(*) as count
            FROM raw_measurements rm
            LEFT JOIN test_results tr ON rm.test_id = tr.test_id
            WHERE tr.test_id IS NULL
            GROUP BY rm.test_id
            ORDER BY rm.test_id
        """)
        orphans = cursor.fetchall()

        if not orphans:
            print("[INFO] No orphaned raw_measurements found!")
            print("[SUCCESS] Database is clean!")
            return

        print(f"\n[WARNING] Found {len(orphans)} unique test_ids with orphaned measurements:")
        total_orphaned = 0
        for test_id, count in orphans:
            print(f"  - {test_id}: {count} measurements")
            total_orphaned += count

        print(f"\n[SUMMARY] Total orphaned measurements: {total_orphaned}")

        # Step 2: Get current counts
        cursor.execute("SELECT COUNT(*) FROM raw_measurements")
        total_before = cursor.fetchone()[0]
        print(f"[INFO] Total raw_measurements before cleanup: {total_before}")

        # Step 3: Delete orphaned records
        print(f"\n[STEP 2] Deleting {total_orphaned} orphaned raw_measurements...")

        cursor.execute("""
            DELETE FROM raw_measurements
            WHERE test_id NOT IN (SELECT test_id FROM test_results)
        """)
        deleted_count = cursor.rowcount
        conn.commit()

        # Step 4: Verify deletion
        cursor.execute("SELECT COUNT(*) FROM raw_measurements")
        total_after = cursor.fetchone()[0]

        print(f"\n[SUCCESS] Cleanup complete!")
        print(f"[INFO] Raw_measurements before: {total_before}")
        print(f"[INFO] Raw_measurements after:  {total_after}")
        print(f"[INFO] Records deleted:         {deleted_count}")

        # Step 5: Check remaining orphans (should be 0)
        cursor.execute("""
            SELECT COUNT(DISTINCT rm.test_id)
            FROM raw_measurements rm
            LEFT JOIN test_results tr ON rm.test_id = tr.test_id
            WHERE tr.test_id IS NULL
        """)
        remaining_orphans = cursor.fetchone()[0]

        if remaining_orphans == 0:
            print("\n[VERIFIED] No orphaned records remaining!")
        else:
            print(f"\n[WARNING] Still have {remaining_orphans} orphaned test_ids!")

        # Step 6: Report test_results without measurements
        print("\n[STEP 3] Checking test_results without measurements...")
        cursor.execute("""
            SELECT tr.test_id, tr.serial_number, tr.status
            FROM test_results tr
            LEFT JOIN raw_measurements rm ON tr.test_id = rm.test_id
            WHERE rm.test_id IS NULL
            ORDER BY tr.created_at DESC
        """)
        tests_without_measurements = cursor.fetchall()

        if tests_without_measurements:
            print(f"\n[INFO] Found {len(tests_without_measurements)} test_results without measurements:")
            print("       (This is normal for tests that ended in ERROR status)")
            for test_id, serial, status in tests_without_measurements:
                print(f"  - test_id: {test_id}, serial: {serial}, status: {status}")
        else:
            print("\n[INFO] All test_results have measurements!")

        print("\n" + "=" * 80)
        print("[DONE] Cleanup complete!")
        print("=" * 80)

    except Exception as e:
        print(f"\n[ERROR] Cleanup failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    # Database path
    db_path = "database/test_data.db"

    cleanup_orphaned_records(db_path)
