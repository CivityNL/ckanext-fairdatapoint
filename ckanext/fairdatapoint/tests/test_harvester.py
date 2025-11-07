# SPDX-FileCopyrightText: 2025 Health-RI
#
# SPDX-License-Identifier: Apache-2.0

import pytest
from unittest.mock import patch, MagicMock

from ckanext.fairdatapoint.harvesters.civity_harvester import CivityHarvester
from ckanext.harvest.model import HarvestObjectExtra as HOExtra


@pytest.fixture
def mock_harvest_source():
    source = MagicMock()
    source.id = "civity-source-id"
    source.url = "http://dummy-url.com"
    source.config = {}
    source.owner_org = "org-id"
    return source


@pytest.fixture
def mock_harvest_job(mock_harvest_source):
    job = MagicMock()
    job.id = "harvest-job-1"
    job.source = mock_harvest_source
    return job


@pytest.fixture
def harvest_object(mock_harvest_source, mock_harvest_job):
    obj = MagicMock()
    obj.id = "harvest-123"
    obj.guid = "dataset=https://fdp.example.org/dataset/abc"
    obj.extras = [HOExtra(key="status", value="new")]
    obj.content = None
    obj.save = MagicMock()
    obj.source = mock_harvest_source
    obj.job = mock_harvest_job
    return obj

@pytest.fixture
def dummy_harvester():
    class DummyFDPHarvester(CivityHarvester):
        def setup_record_provider(self, harvest_url, harvest_config_dict):
            self.record_provider = MagicMock()
            self.record_provider.get_record_by_id = MagicMock()

        def setup_record_to_package_converter(self, harvest_url, harvest_config_dict):
            self.record_to_package_converter = MagicMock()
        @staticmethod
        def _get_user_name():
            return "test-user"

    harvester = DummyFDPHarvester()
    harvester._save_object_error = MagicMock()
    harvester._create_or_update_package = MagicMock(return_value="pkg-123")
    harvester._create_resources = MagicMock(return_value=True)
    return harvester

@pytest.fixture
def configurable_harvester():
    def _create(record_return_value, package_return_value):
        class DummyFDPHarvester(CivityHarvester):
            def setup_record_provider(self, url, config):
                self.record_provider = MagicMock()
                self.record_provider.get_record_by_id = MagicMock(return_value=record_return_value)

            def setup_record_to_package_converter(self, url, config):
                self.record_to_package_converter = MagicMock()
                self.record_to_package_converter.record_to_package= MagicMock(return_value=package_return_value)
        return DummyFDPHarvester()
    return _create

@patch("ckanext.fairdatapoint.harvesters.civity_harvester.HOExtra")
@patch("ckanext.fairdatapoint.harvesters.civity_harvester.HarvestObject")
@patch("ckanext.fairdatapoint.harvesters.civity_harvester.model.Session.query")
def test_gather_stage_creates_new_object(mock_query, mock_HO, mock_HOExtra, dummy_harvester, mock_harvest_job):
    dummy_harvester._get_guids_in_harvest = lambda job: {"new-guid"}
    dummy_harvester._get_guids_to_package_ids_from_database = lambda job: {}

    mock_query.return_value.filter_by.return_value.first.return_value = None

    ho_extra_mock = MagicMock()
    mock_HOExtra.return_value = ho_extra_mock

    mock_obj = MagicMock(id="obj-new-guid")
    mock_HO.return_value = mock_obj

    result = dummy_harvester.gather_stage(mock_harvest_job)

    assert result == ["obj-new-guid"]
    mock_HOExtra.assert_called_once_with(key="status", value="new")
    mock_HO.assert_called_once_with(
        guid="new-guid",
        job=mock_harvest_job,
        extras=[ho_extra_mock],
    )

@patch("ckanext.fairdatapoint.harvesters.civity_harvester.HOExtra")
@patch("ckanext.fairdatapoint.harvesters.civity_harvester.HarvestObject")
def test_gather_stage_creates_change_object(mock_HO, mock_HOExtra, dummy_harvester, mock_harvest_job):
    dummy_harvester._get_guids_in_harvest = lambda job: {"change-guid"}
    dummy_harvester._get_guids_to_package_ids_from_database = lambda job: {
        "change-guid": "pkg-1"
    }

    mock_HOExtra.return_value = "Extra(status=change)"

    mock_obj = MagicMock(id="obj-change-guid")
    mock_HO.return_value = mock_obj

    result = dummy_harvester.gather_stage(mock_harvest_job)

    assert result == ["obj-change-guid"]
    mock_HOExtra.assert_called_once_with(key="status", value="change")
    mock_HO.assert_called_once_with(
        guid="change-guid",
        job=mock_harvest_job,
        package_id="pkg-1",
        extras=["Extra(status=change)"]
    )

@patch("ckanext.fairdatapoint.harvesters.civity_harvester.HOExtra")
@patch("ckanext.fairdatapoint.harvesters.civity_harvester.HarvestObject")
@patch("ckanext.fairdatapoint.harvesters.civity_harvester.model.Session.query")
def test_gather_stage_creates_delete_object_and_marks_not_current(mock_query, mock_HO, mock_HOExtra, dummy_harvester, mock_harvest_job):

    # Setup GUIDs
    change_guid = "guid-to-change"
    delete_guid = "guid-to-delete"

    dummy_harvester._get_guids_in_harvest = lambda job: {change_guid}
    dummy_harvester._get_guids_to_package_ids_from_database = lambda job: {
        change_guid: "pkg-change",
        delete_guid: "pkg-delete"
    }

    # Prepare HOExtra mocks
    hoextra_change = MagicMock()
    hoextra_delete = MagicMock()

    def hoextra_side_effect(key, value):
        return hoextra_change if value == "change" else hoextra_delete

    mock_HOExtra.side_effect = hoextra_side_effect

    # Prepare HarvestObject mocks
    ho_change = MagicMock(id="ho-change")
    ho_delete = MagicMock(id="ho-delete")

    def ho_side_effect(**kwargs):
        if kwargs["guid"] == change_guid:
            return ho_change
        else:
            return ho_delete

    mock_HO.side_effect = ho_side_effect

    # Mock query().filter_by().update()
    mock_query_result = MagicMock()
    mock_query.return_value.filter_by.return_value = mock_query_result

    # Act
    result = dummy_harvester.gather_stage(mock_harvest_job)

    # Assert expected harvest object IDs are returned
    assert sorted(result) == sorted(["ho-change", "ho-delete"])

    # Verify creation for change
    mock_HO.assert_any_call(
        guid=change_guid,
        job=mock_harvest_job,
        package_id="pkg-change",
        extras=[hoextra_change]
    )

    # Verify creation for delete
    mock_HO.assert_any_call(
        guid=delete_guid,
        job=mock_harvest_job,
        package_id="pkg-delete",
        extras=[hoextra_delete]
    )

    # Verify current=False set for delete
    mock_query_result.update.assert_called_once_with({"current": False}, False)


def test_fetch_stage_status_delete(dummy_harvester, harvest_object):
    harvest_object.extras = [HOExtra(key="status", value="delete")]
    result = dummy_harvester.fetch_stage(harvest_object)
    assert result is True

def test_fetch_stage_successful_fetch(configurable_harvester, harvest_object):
    harvester = configurable_harvester("<rdf>dummy content</rdf>", configurable_harvester)
    result = harvester.fetch_stage(harvest_object)

    assert result is True
    assert harvest_object.content == "<rdf>dummy content</rdf>"
    harvest_object.save.assert_called_once()

def test_fetch_stage_empty_record(configurable_harvester, harvest_object):
    harvester = configurable_harvester(None, None)
    harvester._save_object_error = MagicMock()
    harvest_object.extras = [HOExtra(key="status", value="change")]

    result = harvester.fetch_stage(harvest_object)

    assert result is False
    harvester._save_object_error.assert_called_once()
    assert "Empty record" in harvester._save_object_error.call_args[0][0]

def test_fetch_stage_save_exception(dummy_harvester, harvest_object):
    harvest_object.save.side_effect = Exception("cannot save")
    dummy_harvester._save_object_error = MagicMock()
    result = dummy_harvester.fetch_stage(harvest_object)

    assert result is False
    dummy_harvester._save_object_error.assert_called_once()
    assert "Error saving harvest object" in dummy_harvester._save_object_error.call_args[0][0]


def test_import_stage_delete_status(dummy_harvester, harvest_object):
    harvest_object.extras = [HOExtra(key="status", value="delete")]
    harvest_object.package_id = "pkg-delete"

    with patch("ckanext.fairdatapoint.harvesters.civity_harvester.toolkit.get_action") as get_action:
        delete_action = MagicMock()
        get_action.return_value = delete_action

        result = dummy_harvester.import_stage(harvest_object)

        assert result is True
        delete_action.assert_called_once()


def test_import_stage_empty_content(dummy_harvester, harvest_object):
    harvest_object.content = None
    result = dummy_harvester.import_stage(harvest_object)
    assert result is False
    dummy_harvester._save_object_error.assert_called_once()


def test_import_stage_conversion_error(dummy_harvester, harvest_object):
    dummy_harvester.setup_record_to_package_converter(harvest_object.source.url, {})
    dummy_harvester.record_to_package_converter.record_to_package.side_effect = Exception("fail")

    result = dummy_harvester.import_stage(harvest_object)
    assert result is False
    dummy_harvester._save_object_error.assert_called_once()


def test_import_stage_success_new_package(dummy_harvester, harvest_object):
    harvester = dummy_harvester
    harvester.setup_record_to_package_converter(harvest_object.source.url, {})
    harvester.record_to_package_converter.record_to_package.return_value = {
        "title": "My Dataset",
        "name": "my-dataset",
        "resources": []
    }

    harvest_object.content = "<rdf>dummy content</rdf>"
    # Ensure _create_or_update_package and _create_resources are mocked for isolation
    harvester._create_or_update_package = MagicMock(return_value="pkg-123")
    harvester._create_resources = MagicMock(return_value=True)

    with patch("ckanext.fairdatapoint.harvesters.civity_harvester.model.Session") as mock_session:
        result = harvester.import_stage(harvest_object)
        assert result is True
        harvester._create_or_update_package.assert_called_once()
        harvester._create_resources.assert_called_once()
        assert harvest_object.current is True
        harvest_object.add.assert_called()
        mock_session.commit.assert_called()


def test_import_stage_success_update(dummy_harvester, harvest_object):
    harvest_object.extras = [HOExtra(key="status", value="change")]
    harvest_object.package_id = "existing-pkg"

    dummy_harvester.setup_record_to_package_converter(harvest_object.source.url, {})
    dummy_harvester.record_to_package_converter.record_to_package.return_value = {
        "title": "My Updated Dataset",
        "resources": []
    }
    harvest_object.content = "<rdf>dummy content</rdf>"

    with patch("ckanext.fairdatapoint.harvesters.civity_harvester.model.Session") as mock_session:
        result = dummy_harvester.import_stage(harvest_object)

        assert result is True
        dummy_harvester._create_or_update_package.assert_called_once()
        dummy_harvester._create_resources.assert_called_once()
        mock_session.commit.assert_called()


def test_import_stage_dataset_links_to_existing_series(configurable_harvester, harvest_object):
    # This test verifies that a dataset can be updated to include a link to an existing dataseries.
    # Note: The reverse (adding datasets to a dataseries) is not handled here.
    dataset_guid = "dataset=https://fdp.example.org/dataset/abc"
    dataseries_guid = "dataseries=https://fdp.example.org/datasetseries/xyz"
    harvest_object.guid = dataset_guid
    harvest_object.extras = [HOExtra(key="status", value="change")]
    harvest_object.package_id = "existing-dataset"
    harvest_object.content = "<rdf>dummy dataset referencing series</rdf>"

    package_to_return = {
        "title": "Updated Dataset",
        "name": "updated-dataset",
        "resources": [],
        "in_series": [dataseries_guid],
        "owner_org": harvest_object.owner_org,
    }

    harvester = configurable_harvester(harvest_object.content, package_to_return)
    harvester._create_or_update_package = MagicMock(return_value="pkg-123")

    with patch("ckanext.fairdatapoint.harvesters.civity_harvester.model.Session") as mock_session, \
         patch("ckanext.fairdatapoint.harvesters.civity_harvester.toolkit.get_action") as mock_get_action:
        mock_query = MagicMock()
        mock_query.join.return_value.filter.return_value.filter.return_value.filter.return_value.all.return_value = [
            (dataseries_guid, "series-xyz")
        ]
        mock_session.query.return_value = mock_query

        result = harvester.import_stage(harvest_object)

        assert result is True
        assert harvest_object.current is True
        harvester._create_or_update_package.assert_called_once()
        updated_pkg = harvester._create_or_update_package.call_args[0][0]
        assert updated_pkg["id"] == "existing-dataset"
        # Ensure that only the dataset receives the in_series update
        assert dataseries_guid in updated_pkg["in_series"]
        mock_session.commit.assert_called()
