import os
import random
import shutil

from tqdm import tqdm


def copy_random_files(
    source_folder: str, destination_folder: str, sample_size: int
) -> None:
    # Ensure the destination folder exists
    os.makedirs(destination_folder, exist_ok=True)

    # Get all files in the source folder
    files = [
        f
        for f in os.listdir(source_folder)
        if os.path.isfile(os.path.join(source_folder, f))
    ]

    # Check if the sample size is larger than the number of available files
    if sample_size > len(files):
        print(
            f"Sample size {sample_size} is larger than available files {len(files)}. "
            f"Reducing sample size."
        )
        sample_size = len(files)

    # Randomly sample files
    sampled_files = random.sample(files, sample_size)

    # Copy each sampled file to the destination folder
    for file in tqdm(sampled_files, desc="Copying files", unit="file"):
        source_path = os.path.join(source_folder, file)
        destination_path = os.path.join(destination_folder, file)
        shutil.copy2(source_path, destination_path)


if __name__ == "__main__":
    from_path = "D:/Backup/Photos/photos/photos"
    to_path = "C:/Users/Ruurd/PycharmProjects/Photos/media/images/1"
    copy_random_files(from_path, to_path, 100)
