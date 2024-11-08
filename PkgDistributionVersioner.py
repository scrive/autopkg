#!/usr/bin/env python3

import os
import subprocess
import xml.etree.ElementTree as ET
from autopkglib import Processor, ProcessorError

__all__ = ["PkgDistributionVersioner"]

class PkgDistributionVersioner(Processor):
    """Extracts the version number from a pkg's Distribution file."""
    description = "Extracts version from a pkg's Distribution file"
    input_variables = {
        "pkg_path": {
            "required": True,
            "description": "Path to the pkg file."
        }
    }
    output_variables = {
        "version": {
            "description": "Version extracted from the Distribution file."
        }
    }

    def main(self):
        pkg_path = self.env["pkg_path"]
        temp_dir = os.path.join(self.env.get("RECIPE_CACHE_DIR", "/tmp"), "pkg_extract")

        # Ensure temp_dir is clean
        if os.path.exists(temp_dir):
            subprocess.run(["rm", "-rf", temp_dir], check=True)
        os.makedirs(temp_dir)

        # Extract the pkg file
        cmd = ["/usr/bin/xar", "-xf", pkg_path, "-C", temp_dir]
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            raise ProcessorError(f"Failed to extract pkg: {e}")

        dist_path = os.path.join(temp_dir, "Distribution")
        if not os.path.exists(dist_path):
            raise ProcessorError("Distribution file not found in pkg.")

        # Parse the Distribution file to get the version
        try:
            tree = ET.parse(dist_path)
            root = tree.getroot()
            # Find the first pkg-ref element with a version attribute
            version = root.find(".//pkg-ref[@version]").attrib.get("version")
            if not version:
                raise ProcessorError("Version attribute not found in Distribution file.")
            self.env["version"] = version
            self.output(f"Found version {version}")
        except ET.ParseError as e:
            raise ProcessorError(f"Failed to parse Distribution file: {e}")

if __name__ == "__main__":
    processor = PkgDistributionVersioner()
    processor.execute_shell()