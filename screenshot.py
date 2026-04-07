"""Take a screenshot of the running NiceGUI app using headless Playwright."""
import subprocess
import sys
import time
import socket

PORT = 8501
SCREENSHOT_PATH = "screenshot.png"


def is_port_open():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", PORT)) == 0


def main():
    # Start the app in background, suppressing Qt errors
    env = {**__import__("os").environ, "QT_QPA_PLATFORM": "offscreen"}
    proc = subprocess.Popen(
        [sys.executable, "flexjason.pyw"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
    )

    # Wait for server to actually serve HTTP
    import urllib.request
    print("Waiting for server to start...")
    for _ in range(30):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}", timeout=1)
            break
        except Exception:
            time.sleep(1)
    else:
        print("Server didn't start in time.")
        proc.terminate()
        return

    print("Server is up. Taking screenshot...")
    time.sleep(2)  # let the page render

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(f"http://127.0.0.1:{PORT}", wait_until="networkidle")
        page.wait_for_timeout(3000)  # extra time for JS/CSS to settle
        page.screenshot(path=SCREENSHOT_PATH)
        browser.close()

    print(f"Screenshot saved to {SCREENSHOT_PATH}")
    proc.terminate()


if __name__ == "__main__":
    main()
