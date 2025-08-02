import os
import shutil
import pandas as pd
from collections import Counter
import xml.etree.ElementTree as ET
import pandas as pd

ethnicity_mapping = {
    1: 'African American',
    2: 'Asian Indian',
    3: 'Caucasian Latin',
    4: 'East Asian'
}

def data_exploration(df: pd.DataFrame):
    # Count the number of individuals per ethnic category
    ethnicity_counts = df_labels['ethnicity_name'].value_counts()
    total_individuals = len(df_labels)

    # Calculate percentages
    ethnicity_percentages = (ethnicity_counts / total_individuals) * 100

    print("Ethnic Category Representation among the IDs:")
    print(ethnicity_counts)
    print("\nPercentages:")
    print(ethnicity_percentages)

def dataset_summary(subset_info: dict):
    print("\nSubset Dataset Summary:")
    subset_df = pd.DataFrame(subset_info)
    subset_summary = subset_df.groupby('ethnicity').agg(
        total_individuals=('person_id', 'nunique'),
        total_images=('num_images', 'sum')
    )
    print(subset_summary)

def verify_dataset(people_per_ethnicity: dict, destination_dir: str, destination_file: str):
    person_code = []
    label = []

    print("\nVerifying the dataset structure:")
    print(people_per_ethnicity)
    for ethnicity in people_per_ethnicity.keys():
        eth_dir = os.path.join(destination_dir, ethnicity)
        if os.path.isdir(eth_dir):
            num_ids = len(os.listdir(eth_dir))
            print(f"Ethnicity '{ethnicity}' has {num_ids} individuals.")
            for person_id in os.listdir(eth_dir):
                person_dir = os.path.join(eth_dir, person_id)
                num_images = len(os.listdir(person_dir))
                print(f" - ID {person_id} has {num_images} images.")
                for i in range(num_images):
                    name.append(person_id)
                    label.append(ethnicity)
    # make corresponding csv
    dic_w_labels = {'id': person_code, 'ethnicity': label}
    df = pd.DataFrame(data=dic_w_labels)
    df.to_csv(f'{destination_dir}/{destination_file}', index=False)

def make_dataset(
    labels_file: str,
    images_dir: str,
    destination_dir: str, 
    destination_file: str,
    ethnicity_mapping: dict,
    people_per_ethnicity: dict,
    images_per_person: int
):
    """
    @param labels_file: the name of the file with labels (including the path)
    @param images_dir: directory where images are stored
    @param destination_dir: string with the name of the directory we are creating
    @param distination_file: name of the csv file to which we save [id. label]
    @param ethnicity_mapping: mapping of ethnicity codes to names
        (inside that directory we have images)
    @param people_per_ethnicity: dictionary of how many people per class
    @param images_per_person: how many images a class in the dataset should have
    """
    # create a dataframe for labels
    df_labels = pd.read_xml(labels_file, parser='lxml')
    df_labels['ethnicity_name'] = df_labels['ethnicity'].map(ethnicity_mapping)
    #create a dataframe for images
    train_ids = [name for name in os.listdir(images_dir) if os.path.isdir(os.path.join(images_dir, name))]
    train_ids = sorted(train_ids)
    print(df_labels.head(2))
    print('--------------------------------------')
    # cross reference labels dataframe with image labels
    df_labels = df_labels[df_labels['id'].isin(train_ids)]
    #df_labels['id'] = df_labels['id'].apply(lambda x: int(x[1:]))

    os.makedirs(destination_dir, exist_ok=True)  # ensure destination directory exists
    subset_info = []  # prepare for data collection about the subset

    for ethnicity, num_people in people_per_ethnicity.items():
        ids_in_ethnicity = df_labels[df_labels['ethnicity_name'] == ethnicity]['id'].tolist()

        if len(ids_in_ethnicity) < num_people:
            print(f"Warning: Only {len(ids_in_ethnicity)} individuals available for ethnicity '{ethnicity}'. Adjusting to {len(ids_in_ethnicity)}.")
            num_people = len(ids_in_ethnicity)

        selected_ids = ids_in_ethnicity[:num_people]
        for person_id in selected_ids:
            person_dir = os.path.join(images_dir, str(person_id))
            if not os.path.isdir(person_dir):
                print(f"Warning: Directory {person_dir} does not exist.")
                continue

            image_files = [f for f in os.listdir(person_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if not image_files:
                print(f'No images found for ID {person_id} in ethnicity {ethnicity}.')
                continue

            # select images for a person and copy them to desitnation directory
            num_images = min(images_per_person, len(image_files))
            selected_images = image_files[:num_images]
            dest_person_dir = os.path.join(destination_dir, person_id)
            os.makedirs(dest_person_dir, exist_ok=True)

            for image_file in selected_images:
                src_path = os.path.join(person_dir, image_file)
                dest_path = os.path.join(dest_person_dir, image_file)
                shutil.copy(src_path, dest_path)

                # record the subset info
                subset_info.append({
                    'ethnicity': ethnicity,
                    'person_id': person_id,
                    'num_images': num_images
                })

            dataset_summary(subset_info)
            verify_dataset(people_per_ethnicity, destination_dir, destination_file)
