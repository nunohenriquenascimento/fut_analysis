"""Railway entrypoint. One worker; migrations are deliberately manual."""
import os

import uvicorn


def main():
    try:
        port = int(os.environ.get("PORT", "8000"))
    except ValueError:
        raise SystemExit("PORT must be an integer between 1 and 65535") from None
    if not 1 <= port <= 65535:
        raise SystemExit("PORT must be an integer between 1 and 65535")
    # Do not trust arbitrary forwarded IPs for the login throttle.
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, workers=1, proxy_headers=False)


if __name__ == "__main__":
    main()
