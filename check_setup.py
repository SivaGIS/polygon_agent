"""Run this first: confirms your Python and library versions work for this project."""
import platform
import sys

ok = True
v = sys.version_info
print(f"Python {v.major}.{v.minor}.{v.micro} on {platform.system()} {platform.release()}")
if v < (3, 10):
    print("  !! Python 3.10 or newer is required (3.12-3.14 tested)")
    ok = False
if sys.platform == "darwin" and v >= (3, 13):
    print("  !! On macOS 12 use Python 3.12 (pyproj 3.6.1 has no Python 3.13 build)")
    ok = False
if sys.prefix == sys.base_prefix:
    print("  !! The virtual environment is NOT active -- activate .venv first")
    ok = False

for name in ["anthropic", "shapely", "pyproj", "numpy", "dotenv", "model2vec"]:
    try:
        mod = __import__(name)
        print(f"  {name:10} {getattr(mod, '__version__', 'installed')}")
    except ImportError:
        print(f"  !! {name} missing -- run: pip install -r requirements.txt")
        ok = False

try:
    import shapely
    if int(shapely.__version__.split(".")[0]) < 2:
        print("  !! shapely must be 2.0 or newer")
        ok = False
except ImportError:
    pass

print("\nAll good -- go to week1" if ok else "\nFix the items marked !! above.")
