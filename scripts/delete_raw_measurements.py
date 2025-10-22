"""
Delete raw measurements from database starting from ID 129

This script deletes raw measurement records with ID >= 129 from the database.
"""

import asyncio
import sqlite3
from pathlib import Path


async def delete_raw_measurements(db_path: str, start_id: int = 129):
    """
    Delete raw measurements from database starting from specified ID

    Args:
        db_path: Path to SQLite database file
        start_id: Starting ID to delete from (inclusive)
    """
    db_file = Path(db_path)

    if not db_file.exists():
        print(f"❌ Database file not found: {db_path}")
        return

    print(f"📊 Database: {db_path}")
    print(f"🗑️  Deleting raw_measurements with ID >= {start_id}")

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

        print(f"📈 Total records before: {total_before}")
        print(f"🗑️  Records to delete: {count_to_delete}")

        if count_to_delete == 0:
            print("✅ No records to delete")
            return

        # Get sample of records to be deleted
        cursor.execute(
            "SELECT id, test_id, serial_number, timestamp FROM raw_measurements "
            "WHERE id >= ? ORDER BY id LIMIT 5",
            (start_id,)
        )
        samples = cursor.fetchall()

        print("\n📋 Sample of records to be deleted:")
        for record in samples:
            print(f"   ID: {record[0]}, test_id: {record[1]}, serial: {record[2]}, time: {record[3]}")

        # Confirm deletion
        print(f"\n⚠️  About to DELETE {count_to_delete} records with ID >= {start_id}")
        confirm = input("❓ Continue? (yes/no): ").strip().lower()

        if confirm != "yes":
            print("❌ Deletion cancelled")
            return

        # Delete records
        cursor.execute("DELETE FROM raw_measurements WHERE id >= ?", (start_id,))
        conn.commit()

        # Get total count after deletion
        cursor.execute("SELECT COUNT(*) FROM raw_measurements")
        total_after = cursor.fetchone()[0]

        print(f"\n✅ Deletion complete!")
        print(f"📈 Total records after: {total_after}")
        print(f"🗑️  Records deleted: {total_before - total_after}")

    except Exception as e:
        print(f"❌ Error during deletion: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    # Database path
    db_path = "database/test_data.db"

    # Run deletion
    asyncio.run(delete_raw_measurements(db_path, start_id=129))
