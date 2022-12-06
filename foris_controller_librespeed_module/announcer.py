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

import datetime
import time
import typing


def time_message() -> dict:
    return {
        "module": "librespeed",
        "action": "announce_time",
        "kind": "notification",
        "data": {"timestamp": time.mktime(datetime.datetime.utcnow().timetuple())},
    }


def make_time_message() -> typing.Tuple[int, typing.Callable[[], typing.Optional[dict]]]:

    # returns announcer period announcement will be triggered every n-th second
    return (2, time_message)
