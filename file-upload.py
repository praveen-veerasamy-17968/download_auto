from selenium import webdriver  
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import os
import crome_webdriver
import requests 
import time
import platform
from selenium.webdriver.common.action_chains import ActionChains
import threading

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-minimized")

    # Detect the operating system and set the path accordingly
    if platform.system() == "Windows":
        service = Service(executable_path="driver/chromedriver.exe")
    else :  
        service = Service(executable_path="driver/chromedriver")
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def download_videos(url, filename, driver):
    if not os.path.exists('videos'):
        os.makedirs('videos')
        
    file_path = os.path.join('videos', filename)
    
    def download():
        try:
            print(f"Downloading: {filename}")
            os.system(f"curl -o {file_path} {url}")
        except Exception as e:
            print(f"Error Downloading {filename}: {e}")

    download_thread = threading.Thread(target=download)
    download_thread.start()

def close_all_popups(driver: webdriver.Chrome):
    main_window = driver.current_window_handle
    
    for handle in driver.window_handles:
        if handle != main_window:
            driver.switch_to.window(handle)
            driver.close()
    
    driver.switch_to.window(main_window)

def click_on_free_download(driver, streamtape_url):
    driver.set_window_position(500, 100)
    try:
        free_download_button = driver.find_element(By.CSS_SELECTOR, "body > main > div.container > form > div > button.btn.btn-outline-primary.submit-btn.m-2")
        free_download_button.click()
        return True
    except Exception as e:
        print(f"Error clicking on Free Download button: {e}")
        return False
    

def get_download_link(driver: webdriver.Chrome, streamtape_url):
    driver.set_window_position(500, 100)
    driver.get(streamtape_url)
    try:
        if not click_on_free_download(driver, streamtape_url):
            return None, None

        time.sleep(2)  
       
        play_button = driver.find_element(By.CSS_SELECTOR, "#flvplayer_display_button_play")
        play_button.click()
        time.sleep(1)

        h2_element = driver.find_element(By.CSS_SELECTOR, "body > main > div.container > section > div > div.col-12 > form > div.download.mb-4 > div > div > div.col-auto.flex-grow-1.flex-shrink-1 > h1")
        file_name = h2_element.text.strip()
        file_name = file_name.replace(" ", "_")
        print(f"File Name Found: {file_name}")

        video_player = driver.find_element(By.TAG_NAME, 'video')
        time.sleep(1)
        video_url = video_player.get_attribute('src')
        print(f"Download Link Found: {video_url}")

        return file_name, video_url

    except Exception as e:
        print(f"Error extracting file name or download link from {streamtape_url}: {e}")
        return None, None
    
def read_links_from_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    else:
        print(f"{file_path} does not exist.")
        return []

def main():
    driver = setup_driver()
    links = read_links_from_file("file-upload_links.txt")
    
    if os.path.exists("downloaded.txt"):
        with open("downloaded.txt", "r") as f:
            downloaded = f.readlines()
    else:
        downloaded = []

    for i, link in enumerate(links, 1):
        print(f"Processing {i}/{len(links)}: {link}")
        if link in downloaded:
            print(f"{link} has already been downloaded.")
            continue

        file_name, video_url = get_download_link(driver, link)
        if video_url:
            download_videos(video_url, file_name, driver)
            with open("downloaded.txt", "a") as f:
                f.write(link + '\n')
            
    driver.quit()
    
if __name__ == "__main__":
    crome_webdriver.setup_chromedriver()
    main() 