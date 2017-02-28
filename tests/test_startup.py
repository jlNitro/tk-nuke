# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import sys

from tank_test.tank_test_base import TankTestBase
from tank_test.tank_test_base import setUpModule # noqa

import sgtk

import mock


repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
print "tk-nuke repoistory root found at %s." % repo_root


class TestStartup(TankTestBase):
    """
    General fixtures class for testing Toolkit apps
    """

    _mac_mock_hierarchy = {
        "Applications": {
            "Nuke10.0v5": {
                "Hiero10.0v5.app": {},
                "HieroPlayer10.0v5.app": {},
                "Nuke10.0v5 Non-commercial.app": {},
                "Nuke10.0v5.app": {},
                "NukeAssist10.0v5.app": {},
                "NukeStudio10.0v5 Non-commercial.app": {},
                "NukeStudio10.0v5.app": {},
                "NukeX10.0v5 Non-commercial.app": {},
                "NukeX10.0v5.app": {}
            }
        }
    }

    _windows_mock_hiearchy = {
        "C:/": {
            "Program Files": {
                "Nuke10.0v5": {
                    "Nuke10.0.exe": None
                }
            }
        }
    }

    _os_neutral_hierarchy = {
        "win32": _windows_mock_hiearchy,
        "linux2": {},
        "darwin": _mac_mock_hierarchy
    }

    def setUp(self):
        super(TestStartup, self).setUp()

        # Add an environment variable that will allow the fixture to pick up the engine's code.
        patch = mock.patch.dict("os.environ", {"TK_NUKE_REPO_ROOT": repo_root})
        self.addCleanup(patch.stop)
        patch.start()

        self.setup_fixtures()

        # If we are not requesting to run on actual data.
        if "TK_NO_MOCK" not in os.environ:
            self._os_listdir = os.listdir

            patch = mock.patch("os.listdir", wraps=self._os_listdir_wrapper)
            self.addCleanup(patch.stop)
            patch.start()

    def _recursive_split(self, path):
        if path == "/":
            return []
        elif path.endswith(":\\") or path.endswith(":/"):
            return [path]
        else:
            directory, basename = os.path.split(path)
            return self._recursive_split(directory) + [basename]

    def _os_listdir_wrapper(self, directory):
        tokens = self._recursive_split(directory)
        # Start at the root of the mocked file system
        current_depth = self._os_neutral_hierarchy[sys.platform]
        for t in tokens:
            # If this isn't part of our mocked hierarchy, return the real result.
            if t not in current_depth:
                return self._os_listdir(directory)
            # Remember where we are in the current hierarchy.
            current_depth = current_depth[t]

        # We've dug at a depth
        return current_depth.keys()

    def test_nuke10(self):
        self._test_nuke(
            [
                "Nuke 10.0v5", "NukeX 10.0v5", "NukeStudio 10.0v5", "NukeAssist 10.0v5", "Hiero 10.0v5",
                "Nuke 10.0v5 Non-commercial", "NukeX 10.0v5 Non-commercial", "NukeStudio 10.0v5 Non-commercial"
            ],
            "10.0v5"
        )

    def test_nuke9(self):
        self._test_nuke(
            [
                "Nuke 9.0v8", "NukeX 9.0v8", "NukeStudio 9.0v8", "NukeAssist 9.0v8", "Hiero 9.0v8",
                "Nuke 9.0v8 Non-commercial", "NukeX 9.0v8 Non-commercial", "NukeStudio 9.0v8 Non-commercial"
            ],
            "9.0v8"
        )

    def test_nuke8(self):
        self._test_nuke(
            [
                "Nuke 8.0v4", "NukeX 8.0v4", "Nuke 8.0v4 PLE", "NukeAssist 8.0v4"
            ],
            "8.0v4"
        )

    def test_nuke7(self):
        self._test_nuke(
            [
                "Nuke 7.0v10", "NukeX 7.0v10", "Nuke 7.0v10 PLE", "NukeAssist 7.0v10"
            ],
            "7.0v10"
        )

    def test_nuke6(self):
        self._test_nuke([], "6.3v6")

    def _test_nuke(self, expected_variations, expected_version):

        self._nuke_launcher = sgtk.platform.create_engine_launcher(
            self.tk, sgtk.context.create_empty(self.tk), "tk-nuke", [expected_version]
        )
        # Ensure we are getting back the right variations.
        software_versions = self._nuke_launcher.scan_software()

        expected_variations = set(expected_variations)
        found_variations = set(x.display_name for x in software_versions)
        self.assertSetEqual(found_variations, expected_variations)

        # Ensure the icon is correct.
        for x in software_versions:
            file_name = os.path.basename(x.icon)
            if "studio" in x.display_name.lower():
                self.assertEqual(file_name, "icon_studio_256.png")
            elif "hiero" in x.display_name.lower():
                self.assertEqual(file_name, "icon_hiero_256.png")
            elif "nukex" in x.display_name.lower():
                self.assertEqual(file_name, "icon_x_256.png")
            else:
                self.assertEqual(file_name, "icon_256.png")
