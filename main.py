import os
import json
from math import ceil

from seleniumwire import webdriver  # Import from seleniumwire
from selenium.webdriver.chrome.options import Options
import requests
import ray

from models import Thing
from config import START_ID, END_ID, CHUNK_SIZE


ray.init()


def make_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def get_headers(thing_id=2):
    print("getting headers to scrape api like a cheater")
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


def download_images(thing_id, images):
    path = f"things/{thing_id}/images"
    make_dir(path)

    for image in images:
        for version in image["sizes"]:
            if version["type"] == "display" and version["size"] == "large":
                resp = requests.get(version["url"])

                with open(path + "/" + version["url"].split("/")[-1], "wb+") as f:
                    f.write(resp.content)



def download_models(thing_id, models):
    path = f"things/{thing_id}/files"
    make_dir(path)

    for model in models:
        resp = requests.get(model["public_url"])

        with open(path + "/" + model["name"], "wb+") as f:
            f.write(resp.content)


@ray.remote
def fetch(thing_id, headers):
    print("stealing {}".format(thing_id))
    api_url = f"https://api.thingiverse.com/things/{thing_id}"
    tasks = [
        {"filename": "comments.json", "url": api_url + "/root-comments"},
        {"filename": "images.json", "url": api_url + "/images"},
        {"filename": "files.json", "url": api_url + "/files"},
    ]

    resp = requests.get(api_url, headers=headers)

    if resp.status_code == 404:
        return {"id": thing_id, "state": "missing", "name": None, "created_at": None}

    if resp.status_code == 403:
        return {"id": thing_id, "state": "forbidden", "name": None, "created_at": None}

    make_dir(f"things/{thing_id}")

    details = resp.json()
    with open(f"things/{thing_id}/details.json", "w+") as f:
        json.dump(details, f)

    for task in tasks:
        resp = requests.get(task["url"], headers=headers)

        if resp.status_code != 200:
            print(thing_id, task["api_url"], resp.status_code)
            continue

        with open(f"things/{thing_id}/{task['filename']}", "w+") as f:
            json.dump(resp.json(), f)

        if "files" in task["filename"]:
            download_models(thing_id, resp.json())
        if "images" in task["filename"]:
            download_images(thing_id, resp.json())

    return {
        "id": thing_id,
        "state": "success",
        "name": details["name"],
        "created_at": details["added"],
    }


def build_chunks():
    existing_records = list(Thing.select(Thing.id))
    existing_ids = [record.id for record in existing_records]

    naive_range = list(range(START_ID, END_ID))

    diff = list(set(naive_range) - set(existing_ids))

    return [
        diff[i * CHUNK_SIZE:(i * CHUNK_SIZE) + CHUNK_SIZE]
        for i in range(ceil(len(diff) / CHUNK_SIZE))
    ]


def main():
    make_dir("things")


    chunks = build_chunks()

    for chunk in chunks:
        headers = get_headers()

        futures = [fetch.remote(thing_id, headers) for thing_id in chunk]

        results = ray.get(futures)

        Thing.insert_many(results).on_conflict_replace().execute()


main()
