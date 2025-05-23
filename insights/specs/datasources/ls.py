"""
Custom datasources relate to directory list
"""

import json
import os

from insights.core.context import HostContext
from insights.core.dr import get_name
from insights.core.exceptions import SkipComponent
from insights.core.filters import get_filters
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider
from insights.parsers.fstab import FSTab
from insights.specs import Specs


def _list_items(spec):
    """Return a tuple of directories according to the spec filters."""
    filters = sorted(get_filters(spec))
    if filters:
        if len(filters) == 1 and 'R' not in get_name(spec).split('_')[-2]:
            """
            .. note::
                Insert a non-existing directory when there is only ONE target for
                the datasource to list, to make sure the directory be outputted.

                ==============================================================
                # list a single dir '/mnt'
                $ ls -lan /mnt
                total 0
                drwxr-xr-x.  2 0 0   6 Jun 21  2021 .
                dr-xr-xr-x. 17 0 0 224 Apr 17 16:45 ..
                --------------------------------------------------------------
                # list a single dir with this patch
                $ ls -lan /mnt _non_existing_
                ls: cannot access ' _non_existing_': No such file or directory
                /mnt:                      # <--<< the dir is outputted here
                total 0
                drwxr-xr-x.  2 0 0   6 Jun 21  2021 .
                dr-xr-xr-x. 17 0 0 224 Apr 17 16:45 ..
                ==============================================================
            """
            filters.append('_non_existing_')
        return filters
    raise SkipComponent


@datasource(HostContext)
def list_with_la(broker):
    return ' '.join(_list_items(Specs.ls_la_dirs))


@datasource(HostContext)
def list_with_la_filtered(broker):
    return ' '.join(_list_items(Specs.ls_la_filtered_dirs))


@datasource(HostContext)
def list_with_lan(broker):
    filters = set(_list_items(Specs.ls_lan_dirs))
    if 'fstab_mounted.dirs' in filters and FSTab in broker:
        filters.remove('fstab_mounted.dirs')
        for mntp in broker[FSTab].mounted_on.keys():
            mnt_point = os.path.dirname(mntp)
            filters.add(mnt_point) if mnt_point else None
    return ' '.join(sorted(filters))


@datasource(HostContext)
def list_with_lan_filtered(broker):
    return ' '.join(_list_items(Specs.ls_lan_filtered_dirs))


@datasource(HostContext)
def list_with_lanL(broker):
    return ' '.join(_list_items(Specs.ls_lanL_dirs))


@datasource(HostContext)
def list_with_lanR(broker):
    return ' '.join(_list_items(Specs.ls_lanR_dirs))


@datasource(HostContext)
def list_with_lanRL(broker):
    return ' '.join(_list_items(Specs.ls_lanRL_dirs))


@datasource(HostContext)
def list_with_laRZ(broker):
    return ' '.join(_list_items(Specs.ls_laRZ_dirs))


@datasource(HostContext)
def list_with_laZ(broker):
    return ' '.join(_list_items(Specs.ls_laZ_dirs))


@datasource(HostContext)
def list_files_with_lH(broker):
    files = set(_f for _f in _list_items(Specs.ls_lH_files) if not os.path.isdir(_f))
    if files:
        return ' '.join(sorted(files))
    raise SkipComponent


@datasource(HostContext)
def files_dirs_number(broker):
    """Return a dict of file numbers from the spec filter"""
    result = {}
    for item in sorted(get_filters(Specs.files_dirs_number_filter)):
        item = os.path.join(item, '')  # ensure endswith "/", --> directory
        if os.path.exists(item):
            result[item] = dict(files_number=0, dirs_number=0)
            for name in os.listdir(item):
                path = os.path.join(item, name)
                result[item]['files_number'] += 1 if os.path.isfile(path) else 0
                result[item]['dirs_number'] += 1 if os.path.isdir(path) else 0
    if result:
        return DatasourceProvider(
            content=json.dumps(result, sort_keys=True),
            relative_path='insights_datasources/files_dirs_number',
        )
    raise SkipComponent
