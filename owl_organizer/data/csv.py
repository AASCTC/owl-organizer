import csv

def read_metadata_from_csv(file_path, article_id):
    with open(file_path, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["@id"] == article_id:
                return row
    return None

def write_metadata_to_csv(file_path, metadata):
    with open(file_path, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(metadata.keys()))
        writer.writerow(metadata)