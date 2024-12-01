import time
import requests

SELENIUM_URL = "http://selenium:4444/status"

def wait_for_selenium():

    for _ in range(90):
        try:
            response = requests.get(SELENIUM_URL)
            if response:
                print("Selenium is ready!")
                return
        except requests.exceptions.ConnectionError:
            print(f"Selenium is not ready")
        time.sleep(1)
    raise Exception("Selenium did not become ready in time.")

if __name__ == "__main__":
    wait_for_selenium()
