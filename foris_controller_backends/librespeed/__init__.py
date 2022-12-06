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

# import json

from foris_controller_backends.cmdline import BaseCmdLine
from foris_controller_backends.uci import UciBackend, get_option_named

logger = logging.getLogger(__name__)


class LibreSpeedUci:
    ###
    slices = 10
    ###

    def get_slices(self):
        # with UciBackend() as backend:
        #    data = backend.read("librespeed")
        # return int(get_option_named(data, "librespeed", "data", "slices"))
        ###
        return LibreSpeedUci.slices
        ###

    def set_slices(self, slices):
        # with UciBackend() as backend:
        #    backend.set_option("librespeed", "data", "slices", slices)
        ###
        LibreSpeedUci.slices = slices
        ###
        return True


class LibreSpeedCmds(BaseCmdLine):
    ###
    data = [list(e) for e in enumerate([random.randrange(100) for _ in range(LibreSpeedUci.slices)])]
    ###

    def list(self):
        # return json.loads(self._run_command("<command_to_obtain_data>")[1])
        ###
        del LibreSpeedCmds.data[0]
        while len(LibreSpeedCmds.data) < LibreSpeedUci.slices:
            LibreSpeedCmds.data.append([LibreSpeedCmds.data[-1][0] + 1, random.randrange(100)])
        while len(LibreSpeedCmds.data) > LibreSpeedUci.slices:
            del LibreSpeedCmds.data[0]
        return LibreSpeedCmds.data
        ###
