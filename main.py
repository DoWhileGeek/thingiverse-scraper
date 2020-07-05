import os
import json

from seleniumwire import webdriver  # Import from seleniumwire
from selenium.webdriver.chrome.options import Options
import requests
import ray

ray.init()


def build_chunks(start, chunk_size, num_chunks):
    chunks = []
    cursor = start

    for chunk in range(num_chunks):
        chunks.append(list(range(cursor, cursor + chunk_size)))
        cursor += chunk_size

    return chunks


def make_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def get_headers(thing_id=2):
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    try:
        driver = webdriver.Chrome(options=chrome_options)

        driver.get(f"https://www.thingiverse.com/thing:{thing_id}")
        if "404" in driver.title:
            print(f"thing {thing_id} not found")
            return

        details_req = driver.wait_for_request(
            f"https://api.thingiverse.com/things/{thing_id}"
        )

        return details_req.headers

    finally:
        driver.quit()


def download_models(thing_id, models):
    path = f"things/{thing_id}/files"
    make_dir(path)

    for model in models:
        resp = requests.get(model["public_url"])

        with open(path + "/" + model["name"], "wb+") as f:
            f.write(resp.content)


@ray.remote
def fetch(thing_id, headers):
    api_url = f"https://api.thingiverse.com/things/{thing_id}"
    tasks = [
        {"filename": "comments.json", "url": api_url + "/root-comments"},
        {"filename": "images.json", "url": api_url + "/images"},
        {"filename": "files.json", "url": api_url + "/files"},
    ]

    resp = requests.get(api_url, headers=headers)

    if resp.status_code == 404:
        return {"id": thing_id, "state": "missing"}

    make_dir(f"things/{thing_id}")

    details = resp.json()
    with open(f"things/{thing_id}/details.json", "w+") as f:
        json.dump(details, f)

    for task in tasks:
        resp = requests.get(task["url"], headers=headers)

        if resp.status_code != 200:
            continue

        with open(f"things/{thing_id}/{task['filename']}", "w+") as f:
            json.dump(resp.json(), f)

        if "files" in task["filename"]:
            download_models(thing_id, resp.json())

    return {"id": thing_id, "state": "success", "name": details["name"]}


def main():
    make_dir("things")

    headers = get_headers()

    chunks = list(range(1, 20))
    futures = [fetch.remote(chunk, headers) for chunk in chunks]

    print(ray.get(futures))


main()
