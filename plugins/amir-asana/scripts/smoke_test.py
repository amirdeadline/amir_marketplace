"""Quick credential check: confirms the Asana token works."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from asana_connector.client import AsanaClient, AsanaError  # noqa: E402
from asana_connector.config import MissingTokenError  # noqa: E402


def main() -> int:
    try:
        with AsanaClient() as c:
            me = c.me()
    except MissingTokenError as exc:
        print(exc)
        return 1
    except AsanaError as exc:
        print(f"Auth failed — {exc}")
        return 1

    print(f"Logged in as {me.get('name')} ({me.get('email')})")
    workspaces = me.get("workspaces") or []
    names = ", ".join(w.get("name", "?") for w in workspaces) or "none"
    print(f"Workspaces: {names}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
