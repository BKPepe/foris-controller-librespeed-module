#
# foris-controller-librespeed-module
# Copyright (C) 2022 CZ.NIC, z.s.p.o. (http://www.nic.cz/)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#

import json
import shutil
import textwrap
from pathlib import Path

import pytest
from dateutil.parser import parse
from foris_controller_testtools.fixtures import (
    FILE_ROOT_PATH,
    backend,
    infrastructure,
    mosquitto_test,
    start_buses,
    ubusd_test,
    uci_configs_init,
)
from foris_controller_testtools.utils import FileFaker

FAKE_DATA = [
    {
        "time": "2022-01-01T00:00:00.000000000+01:00",
        "server": "Prague, CZ.NIC",
        "speed_download": 23.3,
        "speed_upload": 53.3,
        "ping": 0.57,
        "jitter": 0.87,
    },
    {
        "time": "2022-01-02T00:00:00.000000000+01:00",
        "server": "Prague, CZ.NIC",
        "speed_download": 22.2,
        "speed_upload": 52.2,
        "ping": 0.52,
        "jitter": 0.88,
    },
]


@pytest.fixture(scope="function")
def librespeed_data(request):
    # TODO reformat server section
    base_path = Path("/tmp/librespeed-data")
    shutil.rmtree(base_path, ignore_errors=True)

    base_path.mkdir(parents=True)
    for record in FAKE_DATA:
        date = parse(record["time"])
        path_dir = base_path / f"{date.year}-{date.month:02}"
        path_dir.mkdir(exist_ok=True)
        path = path_dir / f"{record['time']}.json"

        with path.open("w") as f:
            json.dump(record, f)

    yield base_path, FAKE_DATA

    shutil.rmtree(base_path)


def test_settings(uci_configs_init, infrastructure, start_buses):
    notifications = infrastructure.get_notifications()

    res = infrastructure.process_message(
        {
            "module": "librespeed",
            "action": "get_settings",
            "kind": "request",
        }
    )
    assert set(res["data"].keys()) == {"autostart_enabled"}
    new_autostart_enabled = not res["data"]["autostart_enabled"]

    res = infrastructure.process_message(
        {
            "module": "librespeed",
            "action": "update_settings",
            "kind": "request",
            "data": {
                "autostart_enabled": new_autostart_enabled,
            },
        }
    )
    assert res["data"] == {"result": True}

    notifications = infrastructure.get_notifications(notifications)
    assert notifications[-1] == {
        "module": "librespeed",
        "action": "update_settings",
        "kind": "notification",
        "data": {"autostart_enabled": new_autostart_enabled},
    }

    res = infrastructure.process_message(
        {
            "module": "librespeed",
            "action": "get_settings",
            "kind": "request",
        }
    )
    assert res == {
        "module": "librespeed",
        "action": "get_settings",
        "kind": "reply",
        "data": {
            "autostart_enabled": new_autostart_enabled,
        },
    }


def test_get_data(uci_configs_init, infrastructure, start_buses, librespeed_data):
    res = infrastructure.process_message(
        {
            "module": "librespeed",
            "action": "get_data",
            "kind": "request",
        }
    )
    assert set(res["data"].keys()) == {"performed_tests"}


def test_measure(uci_configs_init, infrastructure, start_buses):
    res = infrastructure.process_message(
        {
            "module": "librespeed",
            "action": "measure",
            "kind": "request",
        }
    )
    assert set(res["data"].keys()) == {"async_id"}
