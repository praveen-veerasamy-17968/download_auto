# Open an read the file all_links.txt
with open('all_links.txt', 'r') as f:
    links = f.readlines()

# Iterate over each line and extract the URL
for link in links:
    link = link.strip()
    url = link.split(' ')[1]
    if 'streamtape' in url:
        with open('streamtape_links.txt', 'a') as f:
            f.write(url + '\n')
    elif 'videzz' in url:
        with open('vidoza_links.txt', 'a') as f:
            f.write(url + '\n')
    elif 'file-upload' in url:
        with open('file-upload_links.txt', 'a') as f:
            f.write(url + '\n')
    else:
        print(f"Unknown URL: {url}")