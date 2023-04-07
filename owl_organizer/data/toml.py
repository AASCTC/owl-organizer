import toml

def read_metadata_from_toml(file_path):
    with open(file_path, "r") as file:
        data = toml.load(file)
        return data
    return None

def write_metadata_to_toml(file_path, metadata):
    with open(file_path, "w") as file:
        toml.dump(metadata, file)
