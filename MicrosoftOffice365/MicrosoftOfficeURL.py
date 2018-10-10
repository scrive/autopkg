#!/usr/bin/env python
#
# Copyright 2018 Tim Ellis
# Loosely based on MSOffice2016URLandUpdateInfoProvider by Allister Banks and Tim Sutton
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

import xml.etree.ElementTree as ET
import urllib2

from autopkglib import Processor, ProcessorError

__all__ = ["MicrosoftOfficeURL"]

BASE_URL = "https://macadmins.software/latest.xml"

class MicrosoftOfficeURL(Processor):
	"""Provides a download URL for different types of Office installer packages."""
	input_variables = {
		"product": {
			"required": True,
			"description": "Name of product to fetch, e.g. office.suite.365, excel.standalone.2016, autoupdate.standalone etc.",
		}
	}
	output_variables = {
		"url": {
			"description": "URL to the latest installer.",
		},
		"version": {
			"description": "The version of the update as extracted from the Microsoft metadata.",
		}
	}

	def get_installer_info(self):
		"""Gets installer information from macadmins.software"""
		# Get metadata URL
		self.output("Requesting xml: %s" % BASE_URL)
		req = urllib2.Request(BASE_URL)

		try:
			fdesc = urllib2.urlopen(req)
			data = fdesc.read()
			fdesc.close()
		except BaseException as err:
			raise ProcessorError("Can't download %s: %s" % (BASE_URL, err))

		root = ET.fromstring(data)
		for package in root.findall("package"):
			id = package.find("id").text
			if id == "com.microsoft." + self.env["product"]:
				self.output("Found package matching: %s" % self.env["product"])
				unclean_version = package.find("version").text
				unclean_version_array = unclean_version.split(' ')
				self.env["version"] = unclean_version_array[0]
				self.env["url"] = package.find("download").text

	def main(self):
		"""Get information about an update"""
		self.get_installer_info()


if __name__ == "__main__":
	PROCESSOR = MicrosoftOfficeURL()
	PROCESSOR.execute_shell()
