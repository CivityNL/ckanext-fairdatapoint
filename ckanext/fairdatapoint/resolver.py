# SPDX-FileCopyrightText: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import logging

from rdflib import RDFS, SDO, SKOS, Graph, URIRef
import re
import requests
from ckanext.fairdatapoint.harvesters.config import get_bioportal_api_key

log = logging.getLogger(__name__)


# Default language for a label if it is not defined (Literal without language tag)
DEFAULT_LABEL_LANG = "en"
LANG_LIST = ["en", "nl"]
SKIP_URIS = []


class resolvable_label_resolver:
    """Generic label resolver class

    This class implements a generic label resolver. It consists of three functions:
    1. load_graph
    2. literal_dict_from_graph
    3. load_and_translate_uri

    The functions are made for the generic case: assuming the subject URI is resolvable and will
    return an RDF document when accessed using content negotiation. This can work for some of the
    European labels (HVD themes for example) and also for Wikidata.

    Some ontologies (e.g. SNOMED-CT) don't have resolvable URIs, in that case an OWL ontology would
    have to be loaded first. For these cases, all you'd have to do is override the load_graph
    function in a subclass to point to the OWL ontology to load. There you could also implement
    some caching to make sure it doens't keep trying to load 1 million triples for every label.
    """

    label_graph = Graph()

    def literal_dict_from_graph(self, subject: str | URIRef) -> dict:
        """Turns a Graph into a dictionary with key: language, value: label

        This function traverses Graph g to find the labels for a given subject.
        It looks at the following namespaces in order:
            1. Schema.org name
            2. RDF-scheme label
            3. SKOS prefLabel

        All found labels and languages are stored in a dictionary. See this example for the format:
        ```
        {
          "nl": "Albus Perkamentus",
          "en": "Albus Dumbledore"
        }
        ```

        Literals without a language tag are normalized to `DEFAULT_LABEL_LANG`. Only languages
        present in `LANG_LIST` will be included; others are skipped. If there are multiple
        labels for the same language the last one seen will overwrite the previous.

        Parameters
        ----------
        subject : str | URIRef
            subject for which the label is to be extracted

        Returns
        -------
        dict
            Dictionary containing labels with language as key, localized label as value
        """
        lang_dict = dict()
        if not isinstance(subject, URIRef):
            subject = URIRef(subject)

        # I am aware the dictionary gets overwritten. I am assuming SKOS.prefLabel is the most
        # "authortive" one and therefore it will overwrite the preceding labels.
        for label_predicate in [SDO.name, RDFS.label, SKOS.prefLabel]:
            if (subject, label_predicate, None) in self.label_graph:
                # Check if it contains label_predicate for the subject
                for x in self.label_graph.objects(
                    subject=subject,
                    predicate=label_predicate,
                ):
                    # Normalize missing language to DEFAULT_LABEL_LANG
                    lang = x.language or DEFAULT_LABEL_LANG
                    # Only keep languages we explicitly support
                    if lang in LANG_LIST:
                        lang_dict[lang] = x.value

        return lang_dict

    def load_graph(self, uri: str | URIRef, empty_graph: bool = False) -> Graph:
        """Loads graph into the class located at a URI into the class

        Parameters
        ----------
        uri : str | URIRef
            URI of graph to load
        empty_graph : bool, optional
            Empty current graph when loading, by default False

        Returns
        -------
        Graph
            Loaded Graph
        """
        if str(uri) in SKIP_URIS:
            return self.label_graph
        
        if empty_graph:
            del self.label_graph
            self.label_graph = Graph()

        try:
            # Check if 'bioontology' is in the URI because of different request style
            if re.search(r"bioontology.org", str(uri), re.IGNORECASE):
                log.info("BioOntology URI detected: %s", uri)

                ontology = uri.split("/ontology/")[1].split("/")[0]
                encoded_concept = requests.utils.quote(uri, safe='')

                url = f"https://data.bioontology.org/ontologies/{ontology}/classes/{encoded_concept}"
                api_key = get_bioportal_api_key()

                if not api_key:
                    log.error("BioPortal API key is not configured. Cannot fetch data from BioOntology.")
                    SKIP_URIS.append(str(uri))
                    return self.label_graph

                headers = {
                    "Accept": "application/json",  # request JSON-LD
                    "Authorization": f"apikey token={api_key}"
                }
                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    self.label_graph.parse(data=response.text, format="json-ld")
                else:
                    log.error("Failed to fetch data: %s", response.status_code)
                    log.error("Response text: %s", response.text)
                    SKIP_URIS.append(str(uri))
            else:
                self.label_graph.parse(uri)
        # RDFlib can throw a LOT of exceptions and they are not all
        except Exception as e:
            # Check if it's a 404 error. If so, skip retrying
            if "404" in str(e) or "Not Found" in str(e):
                log.error("URI %s returned 404 Not Found. Adding to skip list.", uri)
                SKIP_URIS.append(str(uri))
            else:
                log.warning("Could not load Graph for URI %s. Trying XML format.", uri)
                try:
                    self.label_graph.parse(uri, format="xml")
                except Exception:
                    log.error("Could not load XML Graph for URI %s, because of error: %s", uri, e)
                    SKIP_URIS.append(str(uri))

        return self.label_graph

    def load_and_translate_uri(self, subject_uri: str | URIRef) -> list[dict[str, str]]:
        """Loads the RDF graph for a given subject, extracts labels

        Parameters
        ----------
        subject_uri : str | URIRef
            Subject URI that the labels need to be extracted for

        Returns
        -------
        list[dict[str, str]]
            List of dictionaries in the format of CKAN function `term_translation_update_many`
        """
        self.load_graph(subject_uri)
        translation_dict = self.literal_dict_from_graph(subject_uri)
        ckan_translation_list = []

        """
        Now turn the dictionary into CKAN format
        It should be as follows:

        Parameters:
        term (string) - the term to be translated, in the original language, e.g. 'romantic novel'
        term_translation (string) - the translation of the term, e.g. 'Liebesroman'
        lang_code (string) - the language code of the translation, e.g. 'de'
        """
        for language, label in translation_dict.items():
            # only append allowed languages
            if language and language in LANG_LIST:
                ckan_translation_list.append(
                    {
                        "term": str(subject_uri),
                        "term_translation": label,
                        "lang_code": language,
                    }
                )

        return ckan_translation_list
