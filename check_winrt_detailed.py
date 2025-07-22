import sys
import os

print("=== WinRT Package Investigation ===")
print()

# Check winrt module location
try:
    import winrt
    print(f"✓ winrt module found")
    print(f"  Location: {winrt.__file__ if hasattr(winrt, '__file__') else 'Built-in module'}")
    print(f"  Version: {winrt.__version__ if hasattr(winrt, '__version__') else 'Unknown'}")
    
    # Check attributes
    print("\n  Available attributes:")
    attrs = dir(winrt)
    for attr in attrs[:10]:  # Show first 10
        print(f"    - {attr}")
    if len(attrs) > 10:
        print(f"    ... and {len(attrs) - 10} more")
        
except Exception as e:
    print(f"✗ Error importing winrt: {e}")

print("\n" + "-" * 50)

# Try to find winrt in site-packages
site_packages = next(p for p in sys.path if 'site-packages' in p)
winrt_path = os.path.join(site_packages, 'winrt')

if os.path.exists(winrt_path):
    print(f"\nwinrt directory found at: {winrt_path}")
    print("Contents:")
    try:
        for item in os.listdir(winrt_path)[:10]:
            print(f"  - {item}")
    except:
        pass
else:
    print(f"\nwinrt directory NOT found at: {winrt_path}")

# Check for winrt_runtime
print("\n" + "-" * 50)
try:
    import winrt_runtime
    print(f"✓ winrt_runtime module found")
    print(f"  Location: {winrt_runtime.__file__ if hasattr(winrt_runtime, '__file__') else 'Unknown'}")
except Exception as e:
    print(f"✗ Error importing winrt_runtime: {e}")

# Try different import approaches
print("\n" + "-" * 50)
print("Testing different import approaches:")

# Approach 1: Direct notifications import
try:
    import winrt
    winrt.init_apartment()  # Initialize COM apartment if needed
    print("✓ winrt.init_apartment() successful")
except Exception as e:
    print(f"✗ winrt.init_apartment() failed: {e}")

# Try importing specific modules
print("\nTrying to access notification modules:")
try:
    import winrt
    # Try to access windows module
    if hasattr(winrt, 'windows'):
        print("✓ winrt.windows exists")
    else:
        print("✗ winrt.windows does NOT exist")
        
        # List all winrt attributes that might be relevant
        print("\nAll winrt attributes:")
        for attr in dir(winrt):
            if not attr.startswith('_'):
                print(f"  - {attr}")
except Exception as e:
    print(f"Error accessing winrt attributes: {e}")