#!/usr/bin/env python3
"""
Test UseCase-Only Emergency Stop

This script tests that emergency stop only executes in UseCase contexts,
not in menu contexts.
"""

import subprocess
import sys
import time
import signal
import os

def test_menu_interrupt():
    """Test Ctrl+C in menu - should NOT trigger emergency stop"""
    print("🧪 Testing Menu Interrupt (Should NOT trigger emergency stop)")
    print("=" * 60)
    
    # Set up environment with virtual environment
    env = dict(os.environ)
    env['VIRTUAL_ENV'] = '/home/blessp/my_code/WF_EOL_TESTER/.venv'
    env['PATH'] = '/home/blessp/my_code/WF_EOL_TESTER/.venv/bin:' + env.get('PATH', '')
    
    # Start CLI application
    process = subprocess.Popen(
        [sys.executable, "src/main_cli.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="/home/blessp/my_code/WF_EOL_TESTER",
        env=env
    )
    
    try:
        # Wait for application to start
        time.sleep(2)
        print("📋 CLI started, sending SIGINT to simulate Ctrl+C in menu...")
        
        # Send SIGINT while in menu
        process.send_signal(signal.SIGINT)
        
        # Wait for process to finish
        stdout, stderr = process.communicate(timeout=10)
        
        # Check for emergency stop messages
        emergency_count = stderr.lower().count("executing emergency stop")
        print(f"\n📊 Emergency stop executions found: {emergency_count}")
        
        if emergency_count == 0:
            print("✅ CORRECT: No emergency stop in menu context")
            return True
        else:
            print(f"❌ INCORRECT: Emergency stop executed {emergency_count} times in menu")
            print("\n📝 Last 20 lines of stderr:")
            for line in stderr.split('\n')[-20:]:
                if line.strip():
                    print(f"  {line}")
            return False
        
    except subprocess.TimeoutExpired:
        process.kill()
        print("⏰ Process timeout - killing")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        if process.poll() is None:
            process.kill()
        return False

def test_usecase_interrupt():
    """Test Ctrl+C during UseCase - should trigger emergency stop exactly once"""
    print("\n🧪 Testing UseCase Interrupt (Should trigger emergency stop ONCE)")
    print("=" * 60)
    
    # Set up environment with virtual environment
    env = dict(os.environ)
    env['VIRTUAL_ENV'] = '/home/blessp/my_code/WF_EOL_TESTER/.venv'
    env['PATH'] = '/home/blessp/my_code/WF_EOL_TESTER/.venv/bin:' + env.get('PATH', '')
    
    # Start CLI application
    process = subprocess.Popen(
        [sys.executable, "src/main_cli.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="/home/blessp/my_code/WF_EOL_TESTER",
        env=env
    )
    
    try:
        # Wait for application to start
        time.sleep(2)
        print("📋 CLI started, selecting option 2 (Simple MCU Test)...")
        
        try:
            # Select option 2 (Simple MCU Test)
            process.stdin.write("2\n")
            process.stdin.flush()
            
            # Wait for test to start
            time.sleep(3)
            print("⚠️  Sending SIGINT during UseCase execution...")
            
            # Send SIGINT during UseCase execution
            process.send_signal(signal.SIGINT)
            
            # Give process time to handle signal
            time.sleep(2)
            
            # Try to close stdin to prevent broken pipe
            process.stdin.close()
            
            # Wait for process to finish
            stdout, stderr = process.communicate(timeout=15)
            
        except subprocess.TimeoutExpired:
            # Force kill if still running
            process.kill()
            stdout, stderr = process.communicate()
        except BrokenPipeError:
            # Handle broken pipe gracefully
            stdout, stderr = process.communicate(timeout=15)
        
        # Count emergency stop executions
        emergency_count = stderr.lower().count("executing emergency stop")
        print(f"\n📊 Emergency stop executions found: {emergency_count}")
        
        if emergency_count == 1:
            print("✅ CORRECT: Emergency stop executed exactly once during UseCase")
            return True
        else:
            print(f"❌ INCORRECT: Emergency stop executed {emergency_count} times (expected 1)")
            print("\n📝 Emergency stop related lines:")
            for line in stderr.split('\n'):
                if "emergency stop" in line.lower():
                    print(f"  {line}")
            return False
        
    except subprocess.TimeoutExpired:
        process.kill()
        print("⏰ Process timeout - killing")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        if process.poll() is None:
            process.kill()
        return False

if __name__ == "__main__":
    print("🔧 Activating virtual environment and testing UseCase-only emergency stop...")
    
    results = []
    
    # Test 1: Menu interrupt
    results.append(test_menu_interrupt())
    
    # Test 2: UseCase interrupt  
    results.append(test_usecase_interrupt())
    
    # Summary
    print("\n" + "="*60)
    print("📋 Test Summary:")
    print(f"  Menu Interrupt Test: {'✅ PASS' if results[0] else '❌ FAIL'}")
    print(f"  UseCase Interrupt Test: {'✅ PASS' if results[1] else '❌ FAIL'}")
    
    if all(results):
        print("\n🎉 All tests PASSED! UseCase-only emergency stop works correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests FAILED! Emergency stop logic needs adjustment.")
        sys.exit(1)