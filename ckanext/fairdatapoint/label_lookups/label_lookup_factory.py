from ckanext.fairdatapoint.label_lookups.biontology_label_lookup import BiontologyLabelLookup
from ckanext.fairdatapoint.label_lookups.wikidata_label_lookup import WikidataLabelLookup


class LabelLookupFactory:

    @staticmethod
    def get_label(url, language):
        if url.startswith('http://purl.bioontology.org/'):
            label_lookup = BiontologyLabelLookup()
            result = label_lookup.get_label(url, language)
        elif url.startswith('https://www.wikidata.org/'):
            label_lookup = WikidataLabelLookup()
            result = label_lookup.get_label(url, language)
        else:
            result = url

        return result
