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
from datetime import date

from foris_controller.handler_base import wrap_required_functions
from foris_controller.module_base import BaseModule


class LibreSpeedModule(BaseModule):
    logger = logging.getLogger(__name__)

    def action_get_settings(self, data):
        return self.handler.get_settings()

    def action_update_settings(self, data):
        res = self.handler.update_settings(**data)
        if res:
            self.notify("update_settings", data)
        return {"result": res}

    def action_get_data(self, data):
        months = data.get("months", 2)
        until = date.fromisoformat(data.get("until", date.today().strftime("%Y-%m-%d")))
        return self.handler.get_data(months, until)

    def action_measure(self, data):
        def notify(msg):
            self.notify("measure", msg)

        def exit_notify(msg):
            self.notify("measure", msg)

        return {
            "async_id": self.handler.measure(notify, exit_notify, self.reset_notify)
        }


@wrap_required_functions(
    [
        "get_settings",
        "update_settings",
        "get_data",
        "measure",
    ]
)
class Handler:
    pass
