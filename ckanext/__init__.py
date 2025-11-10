# SPDX-FileCopyrightText: 2023 Civity
#
# SPDX-License-Identifier: AGPL-3.0-only

# encoding: utf-8

# this is a namespace package
try:
    import pkg_resources
    pkg_resources.declare_namespace(__name__)
except ImportError:
    import pkgutil
    __path__ = pkgutil.extend_path(__path__, __name__)
