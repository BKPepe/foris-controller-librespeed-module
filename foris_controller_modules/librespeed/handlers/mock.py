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

import logging
import random
from datetime import date

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from foris_controller.handler_base import BaseMockHandler
from foris_controller.utils import logger_wrapper

from .. import Handler

logger = logging.getLogger(__name__)

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


class MockLibreSpeedHandler(Handler, BaseMockHandler):
    autostart_enabled = True
    server_id = None

    @logger_wrapper(logger)
    def get_settings(self):
        return {
            "autostart_enabled": self.autostart_enabled,
            "server_id": self.server_id,
        }

    @logger_wrapper(logger)
    def update_settings(self, server_id_in_data, autostart_enabled, server_id=None):
        self.autostart_enabled = autostart_enabled
        if server_id_in_data:
            self.server_id = server_id
        return True

    @logger_wrapper(logger)
    def get_data(self, months: int, until: date):
        next_month = until.replace(day=1) + relativedelta(months=1)
        first_month = next_month - relativedelta(months=months)
        return {
            "performed_tests": [
                e
                for e in FAKE_DATA
                if first_month <= parse(e["time"]).date() < next_month
            ]
        }

    @logger_wrapper(logger)
    def measure(self, notify, exit_notify, reset_notify):
        return "%032X" % random.randrange(2**32)
