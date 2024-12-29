import requests
from bs4 import BeautifulSoup
import re
import os
import subprocess
import asyncio
import aiohttp

def get_vidoza_link(url):
    try:
        print(f"Video Link : {url}")
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None, None

    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string
        if title.endswith(' mp4'):
            title = title[:-4]
        if title.startswith('Watch '):
            title = title[6:]
        print(f"Title: {title}")
    except Exception as e:
        print(f"Error parsing HTML for URL {url}: {e}")
        return None, None

    video_link = None
    match = re.search(r'<video[^>]*>\s*<source[^>]+src="([^"]+)"', response.text)
    if match:
        video_link = match.group(1)
    return title, video_link

# Read URLs from the file vidoza_links.txt
with open('vidoza_links.txt', 'r') as f:
    urls = f.readlines()

# Read already downloaded URLs from downloaded.txt
if os.path.exists("downloaded.txt"):
    with open("downloaded.txt", "r") as f:
        downloaded = f.readlines()
else:
    downloaded = []

async def download_video(session, url, title, video_link):
    try:
        print(f"Downloading video from {video_link}")
        async with session.get(video_link) as response:
            response.raise_for_status()
            video_path = os.path.join('videos', f'{title}.mp4')
            with open(video_path, 'wb') as f:
                f.write(await response.read())
        print(f"Downloaded {title}.mp4")

        # Write the URL to the "downloaded.txt" file to keep track of downloaded videos.
        with open("downloaded.txt", "a") as f:
            f.write(url + '\n')
    except Exception as e:
        print(f"Error downloading video from {video_link}: {e}")

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            url = url.strip()
            if url in downloaded:
                print(f"{url} has already been downloaded.")
                continue

            title, video_link = get_vidoza_link(url)
            if not video_link:
                print(f"Could not find video link for {url}")
                continue

            tasks.append(download_video(session, url, title, video_link))

            if len(tasks) >= 5:
                await asyncio.gather(*tasks)
                tasks = []

        if tasks:
            await asyncio.gather(*tasks)

# Run the main function
asyncio.run(main())