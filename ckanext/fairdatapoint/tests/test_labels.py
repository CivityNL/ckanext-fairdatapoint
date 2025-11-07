# SPDX-FileCopyrightText: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: AGPL-3.0-only
from pathlib import Path
from unittest.mock import patch

import pytest
import rdflib
from rdflib import Graph

from ckanext.fairdatapoint.labels import (
    _is_absolute_uri,
    get_list_unresolved_terms,
    resolve_labels,
    terms_in_package_dict,
)

TEST_DATA_DIRECTORY = Path(Path(__file__).parent.resolve(), "test_data")


@pytest.mark.parametrize(
    ["uri", "resolvable"],
    [
        # Regular resolvable URI
        ("http://www.wikidata.org/entity/Q1568346", True),
        # HTTPS uri
        ("https://example.com/example#uri", True),
        # No path
        ("http://example.com", False),
        # Not a URI at all
        ("appelflap", False),
        # Wrong protocol
        ("ftp://ftp.mozilla.org/robots.txt", False),
        # Empty value
        (None, False),
        # Wrong type
        (12123, False),
    ],
)
def test_absolute_uri(uri, resolvable):
    assert _is_absolute_uri(uri) == resolvable


def test_terms_in_package_dict():
    reference_package_dict = {
        "access_rights": [
            "open_access",
            "https://creativecommons.org/publicdomain/zero/1.0/",
        ],
        "theme": "http://publications.europa.eu/resource/authority/data-theme/HEAL",
        "language": [
            "http://id.loc.gov/vocabulary/iso639-1/en",
            "http://id.loc.gov/vocabulary/iso639-1/nl",
        ],
        "has_version": "0.0.1",
    }
    reference_uris = {
        "https://creativecommons.org/publicdomain/zero/1.0/",
        "http://publications.europa.eu/resource/authority/data-theme/HEAL",
        "http://id.loc.gov/vocabulary/iso639-1/en",
        "http://id.loc.gov/vocabulary/iso639-1/nl",
    }

    assert set(terms_in_package_dict(reference_package_dict)) == reference_uris


class TestTermUpdates:

    @patch("ckan.plugins.toolkit.get_action")
    def test_unresolved_URIs(self, get_action):
        known_data = [
            {
                "term": "http://example.com/uri1",
                "term_translation": "moo",
                "lang_code": "en",
            },
        ]

        get_action.return_value.return_value = known_data

        out_list = get_list_unresolved_terms(
            ["http://example.com/uri1", "http://example.com/uri2"]
        )

        get_action.return_value.assert_called_once()
        assert out_list == ["http://example.com/uri2"]


@patch("ckanext.fairdatapoint.labels.terms_in_package_dict")
@patch("ckanext.fairdatapoint.labels.get_list_unresolved_terms")
@patch(
    "ckanext.fairdatapoint.resolver.resolvable_label_resolver.load_and_translate_uri"
)
@patch("ckan.plugins.toolkit.get_action")
def test_resolve_label_happy_flow(
    get_action,
    load_and_translate_uri,
    get_list_unresolved_terms,
    terms_in_package_dict,
):
    # get_list_unresolved_terms.r
    get_list_unresolved_terms.return_value = [
        "http://www.wikidata.org/entity/Q29937289"
    ]
    translation_list = [
        {
            "term": "http://www.wikidata.org/entity/Q29937289",
            "term_translation": "Datenkatalog",
            "lang_code": "de",
        },
        {
            "term": "http://www.wikidata.org/entity/Q29937289",
            "term_translation": "data catalog",
            "lang_code": "en",
        },
        {
            "term": "http://www.wikidata.org/entity/Q29937289",
            "term_translation": "datacatalogus",
            "lang_code": "nl",
        },
    ]
    expected_filtered_translation_list = translation_list[1:]

    load_and_translate_uri.return_value = translation_list
    get_action.return_value.return_value = {"success": "3 updated succesfully"}

    assert resolve_labels({"theme": "http://www.wikidata.org/entity/Q29937289"}) == 3

    get_action.return_value.assert_called_once_with(
        {"ignore_auth": True, "defer_commit": True},
        {"data": expected_filtered_translation_list},
    )
