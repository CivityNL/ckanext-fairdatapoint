# SPDX-FileCopyrightText: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import logging
from urllib.parse import urlparse

from ckan.plugins import toolkit
from rdflib import URIRef

from ckanext.fairdatapoint.resolver import resolvable_label_resolver

log = logging.getLogger(__name__)

PACKAGE_REPLACE_FIELDS = [
    "access_rights",
    "conforms_to",
    "has_version",
    "language",
    "spatial_uri",
    "theme",
    "dcat_type",
    "code_values",
    "coding_system",
    "health_category",
    "health_theme",
    "publisher_type",
    "frequency",
    "qualified_relation_role",
    "type",
    "quality_annotation_body",
    "quality_annotation_target",
    "legal_basis",
    "personal_data",
    "purpose",
]
RESOURCE_REPLACE_FIELDS = [
    "format",
    "language",
    "access_rights",
    "conforms_to",
    "status",
]
ACCESS_SERVICES_REPLACE_FIELDS = [
    "access_rights",
    "conforms_to",
    "format",
    "language",
    "keyword"
]

# Languages to resolve labels in
# TODO language codes should be dynamic
RESOLVE_LANGUAGES = ("en", "nl")


def resolve_labels(package_dict: dict) -> int:
    """Resolves labels and updates the database

    Parameters
    ----------
    package_dict : dict
        Package dictionary from harvester

    Returns
    -------
    int
        Number of successfully resolved labels, -1 if none needed to be resolved

    """
    log.debug("Label resolving is requested")
    translation_list = []

    total_terms = terms_in_package_dict(package_dict)
    unresolved_terms = get_list_unresolved_terms(total_terms)

    if unresolved_terms:
        log.debug("There are %d unresolved terms", len(unresolved_terms))

        resolver = resolvable_label_resolver()

        for term in unresolved_terms:
            extra_translations = resolver.load_and_translate_uri(term)
            translation_list.extend(extra_translations)

        # Check if there is actually translations in the list
        if translation_list:
            log.debug("Resolved %d labels", len(translation_list))

            # term_translation_update is a privileged function
            # Thank god CKAN is like Hollywood OS and we can just override
            # Extra defensive filter: ensure only supported language codes are sent
            filtered_translation_list = [
                t for t in translation_list if t.get("lang_code") in RESOLVE_LANGUAGES
            ]

            if not filtered_translation_list:
                log.debug("No translations in allowed languages to update")
                return 0


            updated_labels = toolkit.get_action("term_translation_update_many")(
                {"ignore_auth": True, "defer_commit": True},
                {"data": filtered_translation_list},
            )

            if "success" not in updated_labels:
                log.warning("Error updating labels: %s", updated_labels)
            else:
                log.debug("Updated %s labels in database", updated_labels["success"])
                return len(translation_list)
        else:
            log.debug("No labels succesfully resolved")
            return 0
    else:
        log.debug("There are no unresolved terms!")
        return -1


def get_list_unresolved_terms(
        terms: list[str], languages: list[str] = RESOLVE_LANGUAGES
) -> list[str]:
    """This function gets a list of terms not fully known by CKAN, based on an input list

    If a label is present in one language but missing in another, it is considered resolved:
    reason being that the language most likely does not exist for a given label, if one was
    resolved successfully before.

    Parameters
    ----------
    terms : list[str]
        List of labels that harvested, that need to be checked if they are resolved
    languages : list[str], optional
        List of language codes that need to be resolved, default is 'en' and 'nl'.

    Returns
    -------
    list[str]
        List containing the labels that are not resolved yet
    """
    term_set = set(terms)

    translation_table = toolkit.get_action("term_translation_show")(
        {}, {"terms": term_set, "lang_codes": languages}
    )

    known_terms = set(x["term"] for x in translation_table)
    unknown_terms = term_set - known_terms

    return list(unknown_terms)


def _is_absolute_uri(uri: str) -> bool:
    """Checks if a given URI is an absolute http or https URI.

    Checks for three things:
    1. Scheme is either `http` or `https`
    2. A netloc is defined (domain name)
    3. A path is defined

    Parameters
    ----------
    uri : str
        URI that needs to be checked

    Returns
    -------
    bool
        True if resolvale URI, False if not
    """
    try:
        # If URI cannot be parsed we can safely assume it's invalid
        parsed_uri = urlparse(uri)
    except (ValueError, AttributeError):
        return False

    parsable = bool(
        parsed_uri.scheme in ["http", "https"] and parsed_uri.netloc and parsed_uri.path
    )
    return parsable


def _append_value(term_list, val):
    # helper to append single or list values
    if isinstance(val, list):
        for v in val:
            if isinstance(v, URIRef):
                term_list.append(str(v))
            elif isinstance(v, str):
                term_list.append(v)
    elif isinstance(val, URIRef):
        term_list.append(str(val))
    elif isinstance(val, str):
        term_list.append(val)
    return term_list


def terms_in_package_dict(package_dict: dict) -> list[str]:
    """Extracts list of all terms from a dictionary that could theoretically be resolved

    Parameters
    ----------
    package_dict : dict
        Package dictionary that is harvested and parsed by a profile

    Returns
    -------
    list[str]
        List of URIs that could theoretically be resolved
    """
    term_list = []

    for key in PACKAGE_REPLACE_FIELDS:
        if values := package_dict.get(key):
            term_list = _append_value(term_list, values)

    # resources can be nested in the package
    resources = package_dict.get("resources")
    if resources and isinstance(resources, list):
        for res in resources:
            if not isinstance(res, dict):
                continue
            for key in RESOURCE_REPLACE_FIELDS:
                if values := res.get(key):
                    term_list = _append_value(term_list, values)

            # access_services can be nested inside resources
            access_services = res.get("access_services")
            if access_services and isinstance(access_services, list):
                for svc in access_services:
                    if not isinstance(svc, dict):
                        continue
                    for key in ACCESS_SERVICES_REPLACE_FIELDS:
                        if values := svc.get(key):
                            term_list = _append_value(term_list, values)

    # Now filter if URI and only return absolute http(s) URIs
    valid_term_list = [term for term in term_list if _is_absolute_uri(term)]
    return valid_term_list
