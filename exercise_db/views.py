from django.shortcuts import render
from django.http import HttpResponse

from slugify import slugify
import requests
import json
import asyncio
from os import listdir

import firebase_admin
from firebase_admin import firestore_async, credentials, storage

import workout_scraper.settings as settings


def create_local_data(data):
    localData = []
    repetitionCheck = []

    for obj in data:
        dataName = slugify(obj["name"])

        if dataName not in repetitionCheck:
            repetitionCheck.append(dataName)
            obj["gifPath"] = "gifs/" + dataName + ".gif"
            localData.append(obj)

    stream = open("exercise_db/data/exercisesFB.json", "w")
    stream.write(json.dumps(localData, indent=4))
    stream.close()
    return localData


def get_data():
    baseURL = settings.API_PATH
    headers = {
        "X-RapidAPI-Key": settings.API_KEY,
        "X-RapidAPI-Host": settings.API_HOST,
    }
    response = requests.get(baseURL, headers=headers)

    stream = open("exercise_db/data/exercisesDB.json", "w")
    stream.write(json.dumps(response.json(), indent=4))
    stream.close()
    return create_local_data(response.json())


def get_local_data():
    stream = open("exercise_db/data/exercisesFB.json", "r")
    localData = json.load(stream)
    stream.close()
    return localData


def download(obj, path):
    uri = obj["gifUrl"]
    filename = path + obj["gifPath"]
    with open(filename, "wb") as f:
        f.write(requests.get(uri).content)


async def download_gifs(data):
    localPath = "exercise_db/data/"
    await asyncio.gather(*[download(obj, localPath) for obj in data])


def verify_download(data):
    filenames = listdir("exercise_db/data/")
    missingFiles = []

    for obj in data:
        dataName = obj["gifPath"]
        if dataName not in filenames:
            missingFiles.append(dataName)

    print(missingFiles)


def upload_gifs(obj, bucket):
    imgPath = "exercise_db/data/" + obj["gifPath"]
    blobPath = obj["gifPath"]
    blob = bucket.blob(blobPath)
    blob.upload_from_filename(imgPath)


async def save_data(data):
    cred = credentials.Certificate("firebase-api-key.json")
    firebase_admin.initialize_app(cred, {"storageBucket": settings.FIREBASE_BUCKET})
    db = firestore_async.client()
    bucket = storage.bucket()

    await asyncio.gather(*[upload_gifs(obj, bucket) for obj in data])

    ref = db.collection("exercises")
    await asyncio.gather(
        *[ref.document(slugify(doc["name"])).set(doc, merge=True) for doc in data]
    )


async def index(request):
    localData = get_data()
    # localData = get_local_data()
    await download_gifs(localData)
    verify_download(localData)
    await save_data(localData)

    return HttpResponse("Success")
