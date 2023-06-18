# Workout Web Scraper

Simple Django API designed to reduce number of third party API calls by using a Firebase environment to store immutable data (json responses, and blobs from download links) for future use by frontend applications. For that the Firebase app must be configured with storage and firestore.

This project is only configured for local use, by commenting the functionalities not desired in a call.

Also due to the limitations of the firebase-admin module, currently there is no method to get the blob download link from the firebase bucket, since all methods available request the data directly from the google cloud services and none of them return the access token, only the public URL.

There are a few workarounds for this problem:

- Allow public use of the bucket, so the contents can be downloaded without an access token
- Create a temporary access token for private downloads
- Use another app with access to the main Firebase SDK to get the links and update the database (This was the chosen approach for this project)

## TODOs for a production app

- Set up different endpoints for each call
- Validate callers from trusted sources by API key
- Clean functions from View.py
- Get blob download link from firebase after bucket upload
- Set up unit tests
