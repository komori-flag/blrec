"""PyInstaller entry point - avoids relative import issues."""
import os
import sys

_src_dir = os.path.join(os.path.dirname(__file__), 'src')
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from blrec.cli.main import main

sys.exit(main())
