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

import pytest

from foris_controller_testtools.fixtures import (
    only_message_buses,
    backend,
    infrastructure,
    notify_api,
)


def test_get_slices(infrastructure):
    res = infrastructure.process_message(
        {"module": "librespeed", "action": "get_slices", "kind": "request"}
    )
    assert "errors" not in res
    assert "data" in res
    assert "slices" in res["data"]


@pytest.mark.parametrize("slices", [10, 15])
def test_set_slices(infrastructure, slices):
    filters = [("librespeed", "set_slices")]

    notifications = infrastructure.get_notifications(filters=filters)
    res = infrastructure.process_message(
        {"module": "librespeed", "action": "set_slices", "kind": "request", "data": {"slices": slices}}
    )
    notifications = infrastructure.get_notifications(notifications, filters=filters)
    assert notifications[-1] == {
        "module": "librespeed",
        "action": "set_slices",
        "kind": "notification",
        "data": {"slices": slices},
    }
    res = infrastructure.process_message(
        {"module": "librespeed", "action": "get_slices", "kind": "request"}
    )
    assert res["data"]["slices"] == slices


@pytest.mark.parametrize("slices", [10, 15])
def test_reload_chart_notification(notify_api, infrastructure, slices):
    filters = [("librespeed", "reload_chart")]
    notify = notify_api
    notifications = infrastructure.get_notifications(filters=filters)
    notify("librespeed", "reload_chart", {})
    notifications = infrastructure.get_notifications(notifications, filters=filters)
    assert notifications[-1] == {
        "module": "librespeed",
        "action": "reload_chart",
        "kind": "notification",
        "data": {},
    }


def test_list(infrastructure):
    res = infrastructure.process_message({"module": "librespeed", "action": "list", "kind": "request"})
    assert "records" in res["data"]


@pytest.mark.only_message_buses(["mqtt"])
def test_timestamp_announcements(infrastructure):
    filters = [("librespeed", "announce_time")]

    notifications = infrastructure.get_notifications([], filters=filters)
    assert "timestamp" in notifications[-1]["data"]
    timestamp1 = notifications[-1]["data"]["timestamp"]

    notifications = infrastructure.get_notifications(notifications, filters=filters)
    assert "timestamp" in notifications[-1]["data"]
    timestamp2 = notifications[-1]["data"]["timestamp"]

    assert timestamp1 < timestamp2
    assert round(timestamp2 - timestamp1, 0) == 2.0  # there is 2s delay in announcer
