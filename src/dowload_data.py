import os
import json
import shutil
import kaggle

# Check if there is already a api key for kaggle
def setup_kaggle_credentials():
    kaggle_dir = os.path.expanduser("~/.kaggle")
    kaggle_json = os.path.join(kaggle_dir, "kaggle.json")

    if os.path.exists(kaggle_json):
        print("Kaggle credentials already exist, skipping setup.")
        return

    print("Kaggle API credentials not found.")
    username = input("Enter your Kaggle username: ").strip()
    key      = input("Enter your Kaggle API key: ").strip()

    os.makedirs(kaggle_dir, exist_ok=True)
    with open(kaggle_json, "w") as f:
        json.dump({"username": username, "key": key}, f)

    os.chmod(kaggle_json, 0o600)
    print(f"Credentials saved to {kaggle_json}")

# dataset runterladen
def download_dataset():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(base_dir, "data", "raw")

    os.makedirs(output_path, exist_ok=True)
    kaggle.api.authenticate()
    kaggle.api.dataset_download_files(
        "tblock/10kgnad",
        path=output_path,
        unzip=True
    )

    to_remove = ["code", "LICENSE", "README.md", "requirements.txt"]
    for name in to_remove:
        full_path = os.path.join(output_path, name)
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        elif os.path.isfile(full_path):
            os.remove(full_path)

    print(f"Download abgeschlossen nach: {output_path}")

if __name__ == "__main__":
    setup_kaggle_credentials()
    download_dataset()