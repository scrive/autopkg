#!/usr/bin/python
#
# Copyright 2010 Per Olofsson (Original Zoom 7z Unarchiver)
# Copyright 2018 Tim Ellis (Zoom IT Unarchiver)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""See docstring for ZoomITUnarchiver class"""

import os
import subprocess
import shutil

from autopkglib import Processor, ProcessorError


__all__ = ["ZoomITUnarchiver"]

EXTNS = {
    'pkg': ['pkg'],
}

class Zoom7zUnarchiver(Processor):
    """Archive decompressor for pkg files, including the Payload."""
    description = __doc__
    input_variables = {
        "archive_path": {
            "required": False,
            "description": "Path to an archive. Defaults to contents of the "
                           "'pathname' variable, for example as is set by "
                           "URLDownloader.",
        },
        "destination_path": {
            "required": False,
            "description": ("Directory where archive will be unpacked, created "
                            "if necessary. Defaults to RECIPE_CACHE_DIR/NAME.")
        },
        "purge_destination": {
            "required": False,
            "description": "Whether the contents of the destination directory "
                           "will be removed before unpacking.",
        },
	}
    output_variables = {
    }

    def main(self):
        """Unarchive a file"""
        # handle some defaults for archive_path and destination_path
        archive_path = self.env.get("archive_path", self.env.get("pathname"))
        if not archive_path:
            raise ProcessorError(
                "Expected an 'archive_path' input variable but none is set!")
        destination_path = self.env.get(
            "destination_path",
            os.path.join(self.env["RECIPE_CACHE_DIR"], self.env["NAME"]))

        # Create the directory if needed.
        if not os.path.exists(destination_path):
            try:
                os.makedirs(destination_path)
            except OSError as err:
                raise ProcessorError("Can't create %s: %s"
                                     % (destination_path, err.strerror))
        elif self.env.get('purge_destination'):
            for entry in os.listdir(destination_path):
                path = os.path.join(destination_path, entry)
                try:
                    if os.path.isdir(path) and not os.path.islink(path):
                        shutil.rmtree(path)
                    else:
                        os.unlink(path)
                except OSError as err:
                    raise ProcessorError("Can't remove %s: %s"
                                         % (path, err.strerror))
		cmd_pkg = ["xar",
				   "-xf",
				   "-C",
				   destination_path,
				   archive_path]

        # Call command.
        try:
            proc = subprocess.Popen(cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            (_, stderr) = proc.communicate()
        except OSError as err:
            raise ProcessorError(
                "%s execution failed with error code %d: %s"
                % (os.path.basename(cmd[0]), err.errno, err.strerror))
        if proc.returncode != 0:
            raise ProcessorError(
                "Unarchiving %s with %s failed: %s"
                % (archive_path, os.path.basename(cmd[0]), stderr))

        self.output("Unarchived %s to %s" % (archive_path, destination_path))

		cmd_payload = ["cd",
			   destination_path,
			   ";",
			   "/usr/bin/gunzip",
			   "-i",
			   "archive_path",
			   "|",
			   "cpio",
			   "-i"]

if __name__ == '__main__':
    PROCESSOR = ZoomITUnarchiver()
    PROCESSOR.execute_shell()
			   