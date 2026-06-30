import urllib.request
import os

file_id = "1DiI_DygJwP9vOnv6XpAwaYkvFC_TcPVs"
download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
output_path = "Abhay_Kumar_Singh_Resume.pdf"

print("Downloading resume from Google Drive...")
try:
    # Set a user-agent to avoid Google blocking the download
    req = urllib.request.Request(
        download_url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req) as response:
        with open(output_path, "wb") as f:
            f.write(response.read())
    print(f"Downloaded successfully to {output_path}")
    print("File size:", os.path.getsize(output_path), "bytes")
except Exception as e:
    print("Error downloading file:", e)
