import json
from schema import ScholarlyArticle, util

def parse_scholarly_article(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
        scholarly_article_schema = ScholarlyArticle(data)
        metadata = util.get_jsonld(scholarly_article_schema)
        return metadata

def write_metadata_to_json(metadata, filename):
    with open(filename, 'w') as f:
        json.dump(metadata, f, indent=4)
