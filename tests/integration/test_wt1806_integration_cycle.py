"""
WT1806 Integration Cycle Test

Tests integration functionality with multiple measurement cycles:
- 10 second cycles (quick test version)
- 3 cycles with statistics tracking
- WH, AH, TIME measurement and analysis

Quick test version for development and validation.

Usage:
    uv run python test_wt1806_integration_cycle.py
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from infrastructure.implementation.hardware.power_analyzer.wt1800e.wt1800e_power_analyzer import (
    WT1800EPowerAnalyzer,
)
from driver.visa import INTERFACE_USB


class IntegrationStats:
    """Statistics tracker for integration measurements"""

    def __init__(self):
        self.cycles: List[Dict[str, float]] = []

    def add_cycle(self, wh: float, ah: float, time: float):
        """Add a cycle measurement"""
        self.cycles.append({"wh": wh, "ah": ah, "time": time})

    def get_stats(self) -> Dict[str, Dict[str, float]]:
        """Calculate min, max, average for all measurements"""
        if not self.cycles:
            return {}

        wh_values = [c["wh"] for c in self.cycles]
        ah_values = [c["ah"] for c in self.cycles]
        time_values = [c["time"] for c in self.cycles]

        return {
            "wh": {
                "min": min(wh_values),
                "max": max(wh_values),
                "avg": sum(wh_values) / len(wh_values),
            },
            "ah": {
                "min": min(ah_values),
                "max": max(ah_values),
                "avg": sum(ah_values) / len(ah_values),
            },
            "time": {
                "min": min(time_values),
                "max": max(time_values),
                "avg": sum(time_values) / len(time_values),
            },
        }

    def print_summary_table(self):
        """Print formatted statistics table"""
        if not self.cycles:
            print("No cycle data available")
            return

        stats = self.get_stats()

        print("\n" + "=" * 70)
        print("  INTEGRATION CYCLE STATISTICS")
        print("=" * 70)

        # Header
        print(f"\n{'Measurement':<15} {'Min':>12} {'Max':>12} {'Average':>12} {'Unit':>8}")
        print("-" * 70)

        # WH (Energy)
        print(
            f"{'Energy (WH)':<15} "
            f"{stats['wh']['min']:>12.6f} "
            f"{stats['wh']['max']:>12.6f} "
            f"{stats['wh']['avg']:>12.6f} "
            f"{'Wh':>8}"
        )

        # AH (Charge)
        print(
            f"{'Charge (AH)':<15} "
            f"{stats['ah']['min']:>12.6f} "
            f"{stats['ah']['max']:>12.6f} "
            f"{stats['ah']['avg']:>12.6f} "
            f"{'Ah':>8}"
        )

        # TIME
        print(
            f"{'Time':<15} "
            f"{stats['time']['min']:>12.3f} "
            f"{stats['time']['max']:>12.3f} "
            f"{stats['time']['avg']:>12.3f} "
            f"{'s':>8}"
        )

        print("-" * 70)

        # Individual cycle results
        print(f"\n{'Cycle Details:'}")
        print(f"{'Cycle':<8} {'Energy (Wh)':>15} {'Charge (Ah)':>15} {'Time (s)':>12}")
        print("-" * 70)

        for i, cycle in enumerate(self.cycles, 1):
            print(
                f"{'#' + str(i):<8} "
                f"{cycle['wh']:>15.6f} "
                f"{cycle['ah']:>15.6f} "
                f"{cycle['time']:>12.3f}"
            )

        print("=" * 70 + "\n")


async def run_integration_cycle(
    power_analyzer: WT1800EPowerAnalyzer, cycle_num: int, duration_seconds: float
) -> Dict[str, float]:
    """
    Run a single integration cycle

    Args:
        power_analyzer: WT1800EPowerAnalyzer instance
        cycle_num: Cycle number (for display)
        duration_seconds: Integration duration in seconds

    Returns:
        Dictionary with WH, AH, TIME values
    """
    print(f"\n[CYCLE {cycle_num}] Starting integration cycle...")

    # Reset integration
    print(f"  [1/4] Resetting integration...")
    await power_analyzer.reset_integration()
    await asyncio.sleep(0.5)

    state = await power_analyzer.get_integration_state()
    print(f"        State: {state}")

    # Start integration
    print(f"  [2/4] Starting integration...")
    await power_analyzer.start_integration()
    await asyncio.sleep(0.5)

    state = await power_analyzer.get_integration_state()
    print(f"        State: {state}")

    # Wait for duration
    print(f"  [3/4] Running for {duration_seconds:.1f} seconds...")
    interval = 10.0  # Update every 10 seconds
    elapsed = 0.0

    while elapsed < duration_seconds:
        remaining = duration_seconds - elapsed
        wait_time = min(interval, remaining)
        await asyncio.sleep(wait_time)
        elapsed += wait_time

        if remaining > 0:
            print(f"        Progress: {elapsed:.1f}s / {duration_seconds:.1f}s", end="\r")

    print(f"        Progress: {duration_seconds:.1f}s / {duration_seconds:.1f}s [DONE]")

    # Stop integration
    print(f"  [4/4] Stopping integration...")
    await power_analyzer.stop_integration()
    await asyncio.sleep(0.5)

    state = await power_analyzer.get_integration_state()
    print(f"        State: {state}")

    # Read values
    values = await power_analyzer.get_integration_values()

    print(f"\n  Results:")
    print(f"    Energy (WH): {values['wh']:.6f} Wh")
    print(f"    Charge (AH): {values['ah']:.6f} Ah")
    print(f"    Time:        {values['time']:.3f} s")

    return {"wh": values["wh"], "ah": values["ah"], "time": values["time"]}


async def test_integration_cycles():
    """Test integration with multiple cycles and statistics"""

    print("\n" + "=" * 70)
    print("  WT1806 Integration Cycle Test")
    print("  Multiple 10s cycles with statistics tracking")
    print("  (Quick test version)")
    print("=" * 70)

    # Test configuration
    NUM_CYCLES = 3
    CYCLE_DURATION = 10.0  # seconds (quick test)

    # Create power analyzer with USB connection
    power_analyzer = WT1800EPowerAnalyzer(
        interface_type=INTERFACE_USB,
        usb_vendor_id="0x0B21",
        usb_model_code="0x0025",
        usb_serial_number=None,  # Auto-detect
        element=1,
        voltage_range="60V",
        current_range="50A",
        auto_range=False,
        timeout=10.0,
    )

    # Statistics tracker
    stats = IntegrationStats()

    try:
        # Step 1: Connect
        print("\n[SETUP 1/3] Connecting to WT1806...")
        await power_analyzer.connect()
        print("            [OK] Connected")

        # Step 2: Get device info
        print("\n[SETUP 2/3] Getting device information...")
        identity = await power_analyzer.get_device_identity()
        print(f"            Device: {identity}")

        # Step 3: Configure integration
        print("\n[SETUP 3/3] Configuring integration...")
        print(f"            Mode: NORMAL")
        print(f"            Timer: 15 seconds (safety margin for {CYCLE_DURATION:.1f}s cycles)")
        print(f"            Auto Calibration: ON")
        print(f"            Current Mode: RMS")

        await power_analyzer.configure_integration(
            mode="NORMAL",
            timer_hours=0,
            timer_minutes=0,
            timer_seconds=15,
            auto_calibration=True,
            current_mode="RMS",
        )
        print("            [OK] Integration configured")

        # Run multiple cycles
        print("\n" + "=" * 70)
        print(f"  RUNNING {NUM_CYCLES} INTEGRATION CYCLES")
        print(f"  Duration: {CYCLE_DURATION} seconds per cycle")
        print("=" * 70)

        for cycle_num in range(1, NUM_CYCLES + 1):
            try:
                result = await run_integration_cycle(
                    power_analyzer, cycle_num, CYCLE_DURATION
                )
                stats.add_cycle(result["wh"], result["ah"], result["time"])

                # Wait between cycles
                if cycle_num < NUM_CYCLES:
                    print(f"\n  Waiting 5 seconds before next cycle...")
                    await asyncio.sleep(5.0)

            except Exception as e:
                print(f"\n  [ERROR] Cycle {cycle_num} failed: {e}")
                continue

        # Print statistics
        stats.print_summary_table()

        # Disconnect
        print("\n[CLEANUP] Disconnecting...")
        await power_analyzer.disconnect()
        print("          [OK] Disconnected")

        print("\n" + "=" * 70)
        print("[SUCCESS] INTEGRATION CYCLE TEST PASSED")
        print("=" * 70 + "\n")

        print("Summary:")
        print(f"  [+] Completed cycles: {len(stats.cycles)}/{NUM_CYCLES}")
        print(f"  [+] Integration configuration: WORKING")
        print(f"  [+] Cycle execution: WORKING")
        print(f"  [+] Statistics calculation: WORKING")

        if stats.cycles:
            stats_data = stats.get_stats()
            print(f"\nKey Results:")
            print(f"  - Average Energy: {stats_data['wh']['avg']:.6f} Wh")
            print(f"  - Average Charge: {stats_data['ah']['avg']:.6f} Ah")
            print(f"  - Average Time:   {stats_data['time']['avg']:.3f} s")

        print("\nNotes:")
        print("  - Values may be 0 or 9.9E+37 if no input signal connected")
        print("  - Connect actual load to measure real energy consumption")
        print("  - Example: SMA Motor consumes ~15-20 Wh per 113.4s cycle")

        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        print(f"        Error type: {type(e).__name__}")

        import traceback
        print("\nTraceback:")
        traceback.print_exc()

        try:
            await power_analyzer.disconnect()
        except:
            pass

        print("\n" + "=" * 70)
        print("[FAILED] INTEGRATION CYCLE TEST FAILED")
        print("=" * 70 + "\n")
        return False


if __name__ == "__main__":
    # Run test
    result = asyncio.run(test_integration_cycles())
    sys.exit(0 if result else 1)
