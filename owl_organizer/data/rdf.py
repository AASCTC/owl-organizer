from rdflib import Graph, Namespace, RDF, Literal

def parse_scholarly_article_rdf(filename):
    # Define the namespaces used in the RDF file
    SCHEMA = Namespace("http://schema.org/")
    DC = Namespace("http://purl.org/dc/elements/1.1/")

    # Load the RDF data into an rdflib Graph object
    g = Graph()
    g.parse(filename)

    # Find the ScholarlyArticle schema in the graph
    for article in g.subjects(RDF.type, SCHEMA.ScholarlyArticle):
        # Extract the metadata from the schema
        metadata = {}
        metadata['@context'] = 'http://schema.org/'
        metadata['@type'] = 'ScholarlyArticle'
        metadata['@id'] = str(article)

        for (predicate, obj) in g.predicate_objects(article):
            if predicate == SCHEMA.author:
                authors = []
                for author in g.objects(article, SCHEMA.author):
                    author_dict = {}
                    for (author_predicate, author_obj) in g.predicate_objects(author):
                        author_dict[str(author_predicate)] = str(author_obj)
                    authors.append(author_dict)
                metadata['author'] = authors
            elif predicate == SCHEMA.datePublished:
                metadata['datePublished'] = str(obj)
            elif predicate == SCHEMA.description:
                metadata['description'] = str(obj)
            elif predicate == SCHEMA.headline:
                metadata['headline'] = str(obj)
            elif predicate == SCHEMA.isPartOf:
                is_part_of_dict = {}
                for (is_part_of_predicate, is_part_of_obj) in g.predicate_objects(obj):
                    is_part_of_dict[str(is_part_of_predicate)] = str(is_part_of_obj)
                metadata['isPartOf'] = is_part_of_dict
            elif predicate == SCHEMA.publisher:
                metadata['publisher'] = str(obj)
            elif predicate == SCHEMA.url:
                metadata['url'] = str(obj)

        return metadata

    raise ValueError("No ScholarlyArticle schema found in RDF file")

def write_metadata_to_rdf(metadata, filename):
    # Define the namespaces used in the RDF file
    SCHEMA = Namespace("http://schema.org/")
    DC = Namespace("http://purl.org/dc/elements/1.1/")

    # Create an rdflib Graph object and add the metadata as an RDF triple
    g = Graph()
    article_node = RDF.URIRef(metadata['@id'])
    g.add((article_node, RDF.type, SCHEMA.ScholarlyArticle))
    for key, value in metadata.items():
        if key == '@id':
            continue
        elif key == 'author':
            for author_dict in value:
                author_node = RDF.BNode()
                g.add((article_node, SCHEMA.author, author_node))
                for author_key, author_value in author_dict.items():
                    g.add((author_node, SCHEMA[author_key], Literal(author_value)))
        elif key == 'isPartOf':
            is_part_of_node = RDF.BNode()
            g.add((article_node, SCHEMA.isPartOf, is_part_of_node))
            for is_part_of_key, is_part_of_value in value.items():
                g.add((is_part_of_node, SCHEMA[is_part_of_key], Literal(is_part_of_value)))
        else:
            g.add((article_node, SCHEMA[key], Literal(value)))

    # Serialize the graph to RDF and write it to a file
    with open(filename, 'wb') as f:
        f.write(g.serialize(format='xml'))

