<!--
SPDX-FileCopyrightText: 2023 Civity 
SPDX-FileContributor: 2024 Stichting Health-RI

SPDX-License-Identifier: CC-BY-4.0
-->

[![REUSE status](https://api.reuse.software/badge/github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-fairdatapoint)](https://api.reuse.software/info/github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-fairdatapoint)
[![Tests](https://github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-fairdatapoint/actions/workflows/test.yml/badge.svg)](https://github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-fairdatapoint/actions/workflows/test.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=GenomicDataInfrastructure_gdi-userportal-ckanext-fairdatapoint&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=GenomicDataInfrastructure_gdi-userportal-ckanext-fairdatapoint)
[![Release](https://github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-fairdatapoint/actions/workflows/release.yml/badge.svg)](https://github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-fairdatapoint/actions/workflows/release.yml)
[![Main](https://github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-fairdatapoint/actions/workflows/main.yml/badge.svg)](https://github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-fairdatapoint/actions/workflows/main.yml)
[![GitHub contributors](https://img.shields.io/github/contributors/GenomicDataInfrastructure/gdi-userportal-ckanext-fairdatapoint)](https://github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-fairdatapoint/graphs/contributors)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)

# ckanext-fairdatapoint

CKAN harvester for [FAIR Data Point](https://www.fairdatapoint.org/). Contains a harvester for FAIR data points. In the future, the FAIR data point API might be supported by this extension too.

## Stages

The harvester runs in three stages. Each of these stages can be modified.

 1. Gather stage. The gather stage uses the FairDataPointRecordProvider which implements the IRecordProvider interface to create a list of identifiers of the objects which should be included in the harvest. In case of a FAIR data point, this list includes catalogs and datasets. In the future, collections could be added;
 2. Fetch stage. The fetch stage downloads the actual source data. In this phase, additional data from other sources may be included to better suit the DCAT profile as expected by CKAN;
 3. Import stage. The import stage does the actual import. How the RDF from the FAIR data point is mapped to CKAN packages and resources is determined by so-called application profiles. In case of a FAIR data point which uses custom fields, a profile must be created. A profile can be defined as a Python class in the ckanext.fairdatapoint.profiles.py file. The new profile must be registered in the [ckan.rdf.profiles] section of setup.py. What profile is being used for a particular is determined by the harvester configuration.

``
{
 "profiles": "fairdatapoint_dcat_ap"
}
``

To run the harvester from the command line:

``
ckan --config=<full path to CKAN ini-file> harvester run-test <id of harvester>
``

To rebuild the index in case it is not automatically update after clearing all packages from a harvester:

``
ckan --config=<full path to CKAN ini-file> search-index rebuild
``

For more information got to [GDI harvester information](https://genomicdatainfrastructure.github.io/gdi-userportal-docs/docs/ckan/harvester/)

## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible? |
|-----------------|-------------|
| 2.10            | tested      |

## Installation

**TODO:** Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install gdi-userportal-ckanext-fairdatapoint:

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

    git clone <https://github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-fairdatapoint.git>
    cd gdi-userportal-ckanext-fairdatapoint
    pip install -e .
 pip install -r requirements.txt

3. Add `fairdatapoint` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     sudo service apache2 reload

## Config settings

### Catalog harvesting

There is a setting `ckanext.fairdatapoint.harvest_catalogs`. Default is `false`. If set to `true`,
CKAN will harvest catalogs as datasets.

The setting can be overriden in the harvester profile, by setting `"harvest_catalogs": "true"` or
`"harvest_catalogs": "false"` in the harvester configuration JSON.

### Label resolving

The harvester supports the resolving of labels for fields defined as a (resolvable) URI. Examples of
this include Wikidata entities. There is a setting `ckanext.fairdatapoint.resolve_labels`. Default
is `true`, but you can disable it globally by explicitly setting it to `false`.

The setting can be overriden in the harvester profile, by setting `"resolve_labels": "true"` or
`"resolve_labels": "false"` in the harvester configuration JSON.

## Developer installation

To install ckanext-fairdatapoint for development, activate your CKAN virtualenv and
do:

    git clone https://github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-fairdatapoint.git
    cd gdi-userportal-ckanext-fairdatapoint
    python setup.py develop
    pip install -r dev-requirements.txt

Fairdatapoint plugin depends on `ckanext-scheming`, `ckanext-harvester` and `ckanext-dcat`. Make sure these are installed,
otherwise run:

```commandline
pip install -e 'git+https://github.com/ckan/ckanext-scheming.git@release-3.0.0#egg=ckanext-scheming[requirements]'
pip install -e 'git+https://github.com/ckan/ckanext-harvest.git@v1.6.0#egg=ckanext-harvest[requirements]'
pip install -e 'git+https://github.com/ckan/ckanext-dcat.git@v2.2.0#egg=ckanext-dcat'
pip install -r https://raw.githubusercontent.com/ckan/ckanext-dcat/v2.2.0/requirements.txt
```

## Tests

To run the tests go to [GDI harvester test information](https://genomicdatainfrastructure.github.io/gdi-userportal-docs/developer-guide/ckan/extension-local-setup-and-testing/)

## Releasing a new version of ckanext-fairdatapoint

If ckanext-fairdatapoint should be available on PyPI you can follow these steps to publish a new version:

1. Update the version number in the `setup.py` file. See [PEP 440](http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers) for how to choose version numbers.

2. Make sure you have the latest version of necessary packages:

    pip install --upgrade setuptools wheel twine

3. Create a source and binary distributions of the new version:

       python setup.py sdist bdist_wheel && twine check dist/*

   Fix any errors you get.

4. Upload the source distribution to PyPI:

       twine upload dist/*

5. Commit any outstanding changes:

       git commit -a
       git push

6. Tag the new release of the project on GitHub with the version number from
   the `setup.py` file. For example if the version number in `setup.py` is
   0.0.1 then do:

       git tag 0.0.1
       git push --tags

## License

This work is licensed under multiple licenses. Because keeping this section up-to-date is challenging, here is a brief summary as of January 2024:

- All original source code is licensed under [AGPL](./LICENSES/AGPL-3.0-only.txt).
- All documentation is licensed under [CC-BY-4.0](./LICENSES/CC-BY-4.0.txt).
- Some configuration and data files are licensed under [CC-BY-4.0](./LICENSES/CC-BY-4.0.txt).
- For more accurate information, check the individual files.
