from __future__ import annotations

import argparse

from src.swynex_automation.config import build_default_config, load_config
from src.swynex_automation.dashboard import create_app


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local SWYNEX reports dashboard")
    parser.add_argument("--config", help="Path to a SWYNEX JSON configuration file")
    parser.add_argument("--host", default="127.0.0.1", help="Dashboard host (default: localhost only)")
    parser.add_argument("--port", type=int, default=5000, help="Dashboard port")
    args = parser.parse_args()

    config = load_config(args.config) if args.config else build_default_config()
    app = create_app(config.report_dir)
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
