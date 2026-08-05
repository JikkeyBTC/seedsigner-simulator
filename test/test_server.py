"""The local isolated server supplies executable JavaScript MIME types."""

import os
import sys
from urllib.request import urlopen

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness
from harness import check, report


def main() -> int:
    with urlopen(f"{harness.BASE_URL}/pyodide/pyodide.js") as response:
        content_type = response.headers.get_content_type()
        check("Pyodide runtime is served as JavaScript",
              content_type in ("text/javascript", "application/javascript"),
              content_type)
    return report()


if __name__ == "__main__":
    sys.exit(main())
