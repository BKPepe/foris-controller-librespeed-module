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
import logging
from datetime import date
from pathlib import Path

from dateutil.relativedelta import relativedelta
from foris_controller_backends.cmdline import AsyncCommand
from foris_controller_backends.files import BaseFile
from foris_controller_backends.uci import (
    UciBackend,
    get_option_named,
    parse_bool,
    store_bool,
)

logger = logging.getLogger(__name__)


class LibreSpeedUci:
    def get_settings(self):
        with UciBackend() as backend:
            backend.add_section("librespeed", "client", "client")
            data = backend.read("librespeed")
            autostart_enabled = parse_bool(
                get_option_named(data, "librespeed", "client", "autostart_enabled", "0")
            )
            server_id = get_option_named(data, "librespeed", "client", "server", "") or None

        return {
            "autostart_enabled": autostart_enabled,
            "server_id": server_id,
        }

    def update_settings(self, server_id_in_data, autostart_enabled, server_id):

        with UciBackend() as backend:
            backend.add_section("librespeed", "client", "client")
            backend.set_option(
                "librespeed",
                "client",
                "autostart_enabled",
                store_bool(autostart_enabled),
            )
            if server_id_in_data:
                if server_id:
                    backend.set_option(
                        "librespeed",
                        "client",
                        "server",
                        server_id,
                    )
                else:
                    backend.del_option(
                        "librespeed",
                        "client",
                        "server",
                        fail_on_error=False,
                    )

        return True

    def get_params(self) -> dict:
        with UciBackend() as backend:
            backend.add_section("librespeed", "client", "client")
            data = backend.read("librespeed")
            data_dir = get_option_named(
                data, "librespeed", "client", "data_dir", "/tmp/librespeed-data/"
            )
        server_id = get_option_named(data, "librespeed", "client", "server", "") or None
        return {
            "data_dir": data_dir,
            "server_id": server_id,
        }


class LibreSpeedData(BaseFile):
    def read_records(self, months: int, until: date):
        until = until.replace(day=1)

        # Get months
        month_range = reversed([until - relativedelta(months=i) for i in range(months)])

        params = LibreSpeedUci().get_params()

        records = []
        for month in month_range:
            month_path = Path(params["data_dir"]) / f"{month.year:04}-{month.month:02}"
            record_files = sorted(month_path.glob("*.json"))
            for record_file in record_files:
                with record_file.open("r") as f:
                    inner_records = json.load(f)
                    for record in inner_records:
                        records.append(
                            {
                                "server": record.get("server", {}).get("name"),
                                "speed_upload": float(record.get("upload", -1)),
                                "speed_download": float(record.get("download", -1)),
                                "ping": float(record.get("ping", -1)),
                                "jitter": float(record.get("jitter", -1)),
                                "time": record.get("timestamp"),
                            }
                        )

        return records


class LibreSpeedCmds(AsyncCommand):
    def measure(self, notify, exit_notify, reset_notify):
        logger.debug("Starting to measure network speed.")

        def handler_exit(process_data):
            exit_notify(
                {"async_id": process_data.id, "passed": process_data.get_retval() == 0}
            )
            logger.debug(
                "Measuring using librespeed finished: (retval=%d)"
                % process_data.get_retval()
            )

        params = LibreSpeedUci().get_params()
        server_args = []
        if params["server_id"] is not None:
            server_args = ["--server", params["server_id"]]

        process_id = self.start_process(
            ["/usr/bin/turris-librespeed", "--data-dir", params["data_dir"]] + server_args,
            [],
            handler_exit,
            reset_notify,
        )

        logger.debug("Measuring network speed started - '%s'." % process_id)
        return process_id
