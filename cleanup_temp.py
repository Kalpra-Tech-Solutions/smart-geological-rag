#!/usr/bin/env python3
"""
Standalone temp file cleanup script for Windows file locking issues
Run this script when you encounter file locking problems
"""

import os
import glob
import time
import subprocess
import sys
from pathlib import Path

def find_process_using_file(filepath):
    """Find which process is using a file (Windows only)"""
    try:
        # Use handle.exe if available (Sysinternals tool)
        result = subprocess.run(
            ['handle', '-p', 'python', filepath], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout
    except:
        pass
    
    try:
        # Alternative: use PowerShell
        ps_command = f'Get-Process | Where-Object {{$_.Path -like "*python*"}}'
        result = subprocess.run(
            ['powershell', '-Command', ps_command], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout
    except:
        pass
    
    return None

def kill_python_processes():
    """Kill all Python processes (use with caution)"""
    try:
        subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                      capture_output=True, timeout=10)
        subprocess.run(['taskkill', '/f', '/im', 'pythonw.exe'], 
                      capture_output=True, timeout=10)
        print("✅ Killed Python processes")
        time.sleep(2)  # Wait for processes to fully terminate
        return True
    except Exception as e:
        print(f"❌ Error killing processes: {e}")
        return False

def cleanup_temp_files(temp_dir="temp", aggressive=False):
    """Clean up stuck temp files with multiple strategies"""
    
    if not os.path.exists(temp_dir):
        print(f"❌ Temp directory '{temp_dir}' doesn't exist")
        return
    
    # Find all temp files
    temp_patterns = [
        os.path.join(temp_dir, "tmp*.pdf"),
        os.path.join(temp_dir, "tmp*.png"),
        os.path.join(temp_dir, "tmp*.jpg"),
        os.path.join(temp_dir, "tmp*.*")
    ]
    
    all_temp_files = []
    for pattern in temp_patterns:
        all_temp_files.extend(glob.glob(pattern))
    
    if not all_temp_files:
        print("✅ No temp files found to clean up")
        return
    
    print(f"📁 Found {len(all_temp_files)} temp files to clean up")
    
    # Strategy 1: Normal deletion with retries
    files_deleted = 0
    files_failed = []
    
    for temp_file in all_temp_files:
        print(f"🔄 Attempting to delete: {os.path.basename(temp_file)}")
        
        deleted = False
        for attempt in range(5):
            try:
                os.unlink(temp_file)
                print(f"✅ Deleted: {os.path.basename(temp_file)}")
                files_deleted += 1
                deleted = True
                break
            except PermissionError:
                if attempt < 4:
                    print(f"   ⏳ Attempt {attempt + 1}: File locked, waiting...")
                    time.sleep(1 + attempt * 0.5)
                else:
                    print(f"   ❌ File still locked after 5 attempts")
                    files_failed.append(temp_file)
            except Exception as e:
                print(f"   ❌ Error: {e}")
                files_failed.append(temp_file)
                break
        
        if not deleted:
            files_failed.append(temp_file)
    
    print(f"\n📊 Results:")
    print(f"✅ Deleted: {files_deleted} files")
    print(f"❌ Failed: {len(files_failed)} files")
    
    # Strategy 2: Aggressive cleanup for failed files
    if files_failed and aggressive:
        print(f"\n🚀 Attempting aggressive cleanup for {len(files_failed)} failed files...")
        
        # Show which processes might be using the files
        for failed_file in files_failed:
            print(f"\n🔍 Checking processes using: {os.path.basename(failed_file)}")
            process_info = find_process_using_file(failed_file)
            if process_info:
                print(f"   Processes found:\n{process_info}")
        
        # Ask user if they want to kill Python processes
        response = input("\n⚠️  Kill all Python processes to free locked files? (y/N): ").lower()
        if response == 'y':
            if kill_python_processes():
                print("\n🔄 Retrying deletion after killing processes...")
                for temp_file in files_failed:
                    try:
                        if os.path.exists(temp_file):
                            os.unlink(temp_file)
                            print(f"✅ Finally deleted: {os.path.basename(temp_file)}")
                    except Exception as e:
                        print(f"❌ Still couldn't delete {os.path.basename(temp_file)}: {e}")
    
    # Strategy 3: Nuclear option - recreate temp directory
    if files_failed and aggressive:
        response = input("\n💥 Nuclear option: Delete and recreate entire temp directory? (y/N): ").lower()
        if response == 'y':
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                time.sleep(2)
                os.makedirs(temp_dir, exist_ok=True)
                print("💥 Nuclear cleanup complete - temp directory recreated")
            except Exception as e:
                print(f"❌ Nuclear cleanup failed: {e}")

def main():
    """Main cleanup function"""
    print("🧹 Smart Geological RAG - Temp File Cleanup Tool")
    print("=" * 50)
    
    # Parse arguments
    aggressive = '--aggressive' in sys.argv or '-a' in sys.argv
    temp_dir = "temp"
    
    # Check if custom temp directory specified
    for arg in sys.argv:
        if arg.startswith('--temp-dir='):
            temp_dir = arg.split('=')[1]
    
    if aggressive:
        print("⚠️  AGGRESSIVE MODE ENABLED")
        print("   This mode may kill Python processes and recreate directories")
        response = input("   Continue? (y/N): ").lower()
        if response != 'y':
            print("❌ Cleanup cancelled")
            return
    
    # Run cleanup
    cleanup_temp_files(temp_dir, aggressive)
    
    print(f"\n🏁 Cleanup complete!")
    if not aggressive:
        print("💡 Tip: Use --aggressive flag for more thorough cleanup")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
