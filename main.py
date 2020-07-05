import os
import time
import json

from seleniumwire import webdriver  # Import from seleniumwire
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")

# Create a new instance of the Firefox driver
driver = webdriver.Chrome(options=chrome_options)

def fetch(thing_id):
    driver.get(f"https://www.thingiverse.com/thing:{thing_id}")
    if "404" in driver.title:
        print(f"thing {thing_id} not found")
        return

    # wait specifically for these javascript fired requests to return
    api_url = f"https://api.thingiverse.com/things/{thing_id}"
    details_req = driver.wait_for_request(api_url)
    file_req = driver.wait_for_request(api_url+"/files")

    details = json.loads(details_req.response.body.decode("utf-8"))
    files = json.loads(file_req.response.body.decode("utf-8"))

    if files and details:
        thing_path = f"things/{thing_id}"

        if not os.path.exists(thing_path):
            os.mkdir(thing_path)

        with open(thing_path + "/details.json", "w+") as f:
            json.dump(details, f)

        with open(thing_path + "/files.json", "w+") as f:
            json.dump(files, f)

    print(f"Assimilated {thing_id}")


def main():
    try:
        if not os.path.exists("things"):
            os.mkdir("things")

        for thing_id in range(1, 101):
            fetch(thing_id)
    finally:
        print("closing browser")
        driver.quit()


main()
