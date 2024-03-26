# coding: utf8

from ckanext.fairdatapoint.label_lookups.label_lookup_factory import LabelLookupFactory


def main():
    endpoints = [
        'http://purl.bioontology.org/ontology/ICD10CM/U07.1',
        'https://publications.europa.eu/resource/authority/language/HRV',
        'https://id.loc.gov/vocabulary/iso639-1/en',
        'https://www.wikidata.org/wiki/Q11000047',
        'http://www.ebi.ac.uk/efo/EFO_0004778'
    ]

    label_lookup_factory = LabelLookupFactory()

    for endpoint in endpoints:
        label = label_lookup_factory.get_label(endpoint, 'en')
        print(endpoint, '-', label)


if __name__ == "__main__":
    main()
