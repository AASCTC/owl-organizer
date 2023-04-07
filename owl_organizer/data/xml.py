import xmlschema
from lxml import etree

def parse_scholarly_article_xml(filename):
    with open(filename, 'r') as f:
        xml_data = f.read()

        # Create an XML schema object and validate the XML data against it
        xsd = xmlschema.XMLSchema('''<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
            <xs:import namespace="http://schema.org/" schemaLocation="https://schema.org/version/latest/schemaorg-current-http.xsd"/>
            <xs:element name="ScholarlyArticle" type="s:ScholarlyArticle"/>
            </xs:schema>''')
        root = etree.fromstring(xml_data.encode('utf-8'))
        if not xsd.is_valid(root):
            raise ValueError("Invalid XML data")

        # Parse the XML data as a ScholarlyArticle schema
        article_schema = xsd.to_dict(root, path='ScholarlyArticle', process_namespaces=True)
        return article_schema

def write_metadata_to_xml(metadata, filename):
    # Create an XML schema object and build an XML document from the metadata dictionary
    xsd = xmlschema.XMLSchema('''<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
        <xs:import namespace="http://schema.org/" schemaLocation="https://schema.org/version/latest/schemaorg-current-http.xsd"/>
        <xs:element name="ScholarlyArticle" type="s:ScholarlyArticle"/>
        </xs:schema>''')
    article_elem = xsd.to_etree(metadata, path='ScholarlyArticle', process_namespaces=True)

    # Write the XML document to a file
    with open(filename, 'wb') as f:
        f.write(etree.tostring(article_elem, pretty_print=True))
