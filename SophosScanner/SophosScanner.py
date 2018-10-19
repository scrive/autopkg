#!/usr/bin/env python
#
# Copyright 2018 Tim Ellis
# Very loosely based on autopkg-virustotalanalyzer by Hannes Juutilainen
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

import os, subprocess

from autopkglib import Processor, ProcessorError

__all__ = ["SophosScanner"]

class SophosScanner(Processor):
	"""Scans recipe files for threats using Sophos Endpoint Protection for macOS"""

	input_variables = {
		"pathname": {
			"required": False,
			"description": "File path to analyse."
		}
	}
	output_variables = {
		"sophos_scanner_summary_result": {
			"description": "Virus scan report.",
		}
	}

	def scan_location(self, input_path):
		args = ['/usr/local/bin/sweep', '-pua', '-ss', '-suspicious', '-nb', '-rec', '-all', '--show-file-details', '--examine-x-bit', '-archive', '-f', '-sc', input_path]
		p = subprocess.Popen(args, stdout=subprocess.PIPE)
		output = p.communicate()[0]
		if len(output) == 0:
			return "No virus or PUAs detected by Sophos."
		return output

	def main(self):
		if os.path.isfile("/usr/local/bin/sweep") != True:
			self.output("Sophos is not installed. Skipping...")
			return

		if self.env.get("SOPHOS_DISABLED", False):
			self.output("Skipped Sophos scan...")
			return

		input_path = self.env.get("pathname", None)
		if not input_path:
			self.output("Skipping Sophos analysis: no input path defined.")
			return

		# Save summary result
		self.env["sophos_scanner_summary_result"] = {
			'summary_text': 'The summary report from the Sophos scan for this recipe is as follows:',
			'report_fields': [
				'scan_path',
				'result',
			],
			'data': {
				'scan_path': os.path.basename(input_path),
				'result': self.scan_location(input_path),
			}
		}

if __name__ == "__main__":
	processor = SophosScanner()
	processor.execute_shell()
