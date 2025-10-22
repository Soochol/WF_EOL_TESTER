"""
Test Foreign Key Enforcement

This script tests that foreign keys are properly enabled with the new DatabaseManager.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from infrastructure.database.db_manager import DatabaseManager


async def test_foreign_key():
    """Test foreign key enforcement"""
    print("=" * 80)
    print("FOREIGN KEY ENFORCEMENT TEST")
    print("=" * 80)

    # Create DatabaseManager
    db_manager = DatabaseManager("database/test_data.db")

    try:
        # Initialize database
        print("\n[STEP 1] Initializing database...")
        await db_manager.initialize()

        # Check foreign key status in new session
        print("\n[STEP 2] Checking foreign key status in new session...")
        async with db_manager.get_session() as session:
            result = await session.execute(
                __import__("sqlalchemy").text("PRAGMA foreign_keys")
            )
            fk_status = result.scalar()

            if fk_status == 1:
                print("[SUCCESS] Foreign keys are ENABLED!")
                print("          New connections will enforce referential integrity.")
            else:
                print("[FAILED] Foreign keys are DISABLED!")
                print("         Event listener may not be working correctly.")

        # Test foreign key constraint enforcement
        print("\n[STEP 3] Testing foreign key constraint...")
        print("         Attempting to insert raw_measurement with non-existent test_id...")

        try:
            async with db_manager.get_session() as session:
                # Try to insert raw_measurement with invalid test_id
                await session.execute(
                    __import__("sqlalchemy").text("""
                        INSERT INTO raw_measurements
                        (test_id, serial_number, timestamp, temperature, position, force)
                        VALUES ('INVALID_TEST_ID', 'SERIAL_001', datetime('now'), 25.0, 100.0, 50.0)
                    """)
                )
                await session.commit()

                print("[FAILED] Foreign key constraint NOT enforced!")
                print("         Invalid data was inserted (this is bad!)")

        except Exception as e:
            print("[SUCCESS] Foreign key constraint ENFORCED!")
            print(f"          Insert rejected with error: {type(e).__name__}")
            print(f"          Error message: {str(e)[:100]}...")

        print("\n" + "=" * 80)
        print("[TEST COMPLETE]")
        print("=" * 80)

    finally:
        await db_manager.close()


if __name__ == "__main__":
    asyncio.run(test_foreign_key())
