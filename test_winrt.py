import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print()

# Test different import methods
print("Testing import methods:")
print("-" * 50)

# Method 1: Direct winrt
try:
    import winrt
    print("✓ import winrt - SUCCESS")
    print(f"  winrt location: {winrt.__file__}")
except Exception as e:
    print(f"✗ import winrt - FAILED: {e}")

# Method 2: winrt.windows
try:
    import winrt.windows
    print("✓ import winrt.windows - SUCCESS")
except Exception as e:
    print(f"✗ import winrt.windows - FAILED: {e}")

# Method 3: Full path
try:
    import winrt.windows.ui.notifications.management
    print("✓ import winrt.windows.ui.notifications.management - SUCCESS")
except Exception as e:
    print(f"✗ import winrt.windows.ui.notifications.management - FAILED: {e}")

# Method 4: Alternative style
try:
    import winrt
    import winrt.windows.ui.notifications
    print("✓ Alternative import style - SUCCESS")
except Exception as e:
    print(f"✗ Alternative import style - FAILED: {e}")

# Method 5: winsdk
try:
    import winsdk
    print("✓ import winsdk - SUCCESS")
except Exception as e:
    print(f"✗ import winsdk - FAILED: {e}")

print()
print("Checking installed packages:")
print("-" * 50)

import subprocess
result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
for line in result.stdout.split('\n'):
    if 'winrt' in line.lower() or 'winsdk' in line.lower():
        print(line)