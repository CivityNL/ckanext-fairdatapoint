from ckanext.fairdatapoint.label_lookups.biontology_label_lookup import BiontologyLabelLookup
from ckanext.fairdatapoint.label_lookups.wikidata_label_lookup import WikidataLabelLookup
from ckanext.fairdatapoint.label_lookups.publications_europa_label_lookup import PublicationsEuropaLabelLookup
from ckanext.fairdatapoint.label_lookups.id_loc_label_lookup import IdLocLabelLookup


class LabelLookupFactory:

    @staticmethod
    def get_label(url, language):
        label_lookup = None

        if url.startswith('http://purl.bioontology.org/'):
            label_lookup = BiontologyLabelLookup()
        elif url.startswith('https://www.wikidata.org/'):
            label_lookup = WikidataLabelLookup()
        elif url.startswith('https://publications.europa.eu/'):
            label_lookup = PublicationsEuropaLabelLookup()
        elif url.startswith('https://id.loc.gov/'):
            label_lookup = IdLocLabelLookup()

        if label_lookup is not None:
            result = label_lookup.get_label(url, language)
        else:
            result = url

        return result
