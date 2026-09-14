import threading
import webbrowser

import uvicorn

from .app import TOKEN, app


def main():
    url = f"http://127.0.0.1:8765/#token={TOKEN}"
    print("\nAuto Shift — private local workspace")
    print("Open this private link on this computer; do not share it:")
    print(url)
    print("Stop the server with Ctrl+C.\n")
    timer = threading.Timer(1.5, lambda: webbrowser.open(url))
    timer.daemon = True
    timer.start()
    uvicorn.run(app, host="127.0.0.1", port=8765, access_log=False)


if __name__ == "__main__":
    main()
