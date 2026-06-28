from monai.apps import download_and_extract
import os

def download_monai_spleen():
    url = "https://msd-for-monai.s3-us-west-2.amazonaws.com/Task09_Spleen.tar"
    dest = os.path.abspath("data/spleen")
    os.makedirs(dest, exist_ok=True)
    download_and_extract(url, dest)


if __name__ == "__main__":
    download_monai_spleen()
