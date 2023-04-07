import yaml

def parse_scholarly_article_yaml(filename):
    with open(filename, 'r') as f:
        yaml_data = f.read()

        # Parse the YAML data as a ScholarlyArticle schema
        article_schema = yaml.safe_load(yaml_data)
        if not isinstance(article_schema, dict) or article_schema.get('@type', '') != 'ScholarlyArticle':
            raise ValueError("Invalid YAML data or schema type")

        return article_schema

def write_metadata_to_yaml(metadata, filename):
    with open(filename, 'w') as f:
        yaml.dump(metadata, f, default_flow_style=False)
