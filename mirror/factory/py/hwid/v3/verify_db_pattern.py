#!/usr/bin/env python2
# Copyright 2014 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


"""Verifies that new commits do not alter existing encoding patterns.

This test may be invoked in multiple ways:
  1. Execute manually. In this case all the v3 projects listed in projects.yaml
     are checked. The test loads and compares new and old databases from HEAD
     and HEAD~1, respectively, in each corresponding branch of each project.
  2. As a pre-submit check in platform/chromeos-hwid repo. In this case only the
     changed HWID databases in each commit are tested.
  3. VerifyParsedDatabasePattern may be called directly by the HWID Server.
"""

import argparse
import logging
import os
import subprocess
import unittest

from six import itervalues
from six.moves import xrange

import factory_common  # pylint: disable=unused-import
from cros.factory.hwid.v3 import common
from cros.factory.hwid.v3.database import Database
from cros.factory.hwid.v3 import hwid_utils
from cros.factory.hwid.v3 import yaml_wrapper as yaml
from cros.factory.utils import process_utils
from cros.factory.utils.schema import SchemaException


class HWIDDBsPatternTest(unittest.TestCase):
  """Unit test for HWID database."""

  def __init__(self, project=None, commit=None):
    super(HWIDDBsPatternTest, self).__init__()
    self.project = project
    self.commit = commit

  def runTest(self):
    hwid_dir = hwid_utils.GetHWIDRepoPath()
    if not os.path.exists(hwid_dir):
      logging.info(
          'ValidHWIDDBsTest: ignored, no %s in source tree.', hwid_dir)
      return

    # Always read projects.yaml from ToT as all projects are required to have an
    # entry in it.
    target_commit = (self.commit or os.environ.get('PRESUBMIT_COMMIT') or
                     'cros-internal/master')
    projects_info = yaml.load(process_utils.CheckOutput(
        ['git', 'show', '%s:projects.yaml' % target_commit], cwd=hwid_dir))

    def TestDatabase(db_path):
      project_name = os.path.basename(db_path)
      if project_name not in projects_info:
        return
      self.assertEqual(projects_info[project_name]['branch'], 'master')
      logging.info('Checking %s:%s...', target_commit, db_path)
      self.VerifyDatabasePattern(hwid_dir, target_commit, db_path)

    if self.project:
      if self.project not in projects_info:
        self.fail('Invalid project %r' % self.project)
      TestDatabase('v3/%s' % self.project)
      return

    files = os.environ.get('PRESUBMIT_FILES')
    if files:
      files = [f.partition('/platform/chromeos-hwid/')[-1]
               for f in files.splitlines()]
    else:
      # If PRESUBMIT_FILES is not found, defaults to test all v3 projects in
      # projects.yaml.
      files = [b['path'] for b in itervalues(projects_info)
               if b['version'] == 3]

    for f in files:
      TestDatabase(f)

  def VerifyDatabasePattern(self, hwid_dir, commit, db_path):
    """Verify the specific HWID database.

    This method checks 2 things:
      1. Verify whether the newest version of the HWID database is compatible
          with the current version of HWID module.
      2. If the previous version of the HWID database exists and is compatible
          with the current version of HWID module, verify whether all the
          encoded fields in the previous version of HWID database are not
          changed.

    Args:
      hwid_dir: Path of the base directory of HWID databases.
      commit: The commit hash value of the newest version of HWID database.
      db_path: Path of the HWID database to be verified.
    """
    # A compatible version of HWID database can be loaded successfully.
    new_db = Database.LoadData(
        process_utils.CheckOutput(['git', 'show', '%s:%s' % (commit, db_path)],
                                  cwd=hwid_dir, ignore_stderr=True))

    try:
      raw_old_db = process_utils.CheckOutput(
          ['git', 'show', '%s~1:%s' % (commit, db_path)], cwd=hwid_dir,
          ignore_stderr=True)
    except subprocess.CalledProcessError as e:
      if e.returncode != 128:
        raise e
      logging.info('Adding new HWID database %s; skip pattern check',
                   os.path.basename(db_path))
      HWIDDBsPatternTest.VerifyNewCreatedDatabasePattern(new_db)
      return

    try:
      old_db = Database.LoadData(raw_old_db)
    except (SchemaException, common.HWIDException) as e:
      logging.warning('The previous version of HWID database %s is an '
                      'incompatible version (exception: %r), ignore the '
                      'pattern check', db_path, e)
      return
    HWIDDBsPatternTest.VerifyParsedDatabasePattern(old_db, new_db)

  @staticmethod
  def VerifyNewCreatedDatabasePattern(new_db):
    if not new_db.can_encode:
      raise common.HWIDException(
          'The new HWID database should not use legacy pattern.  Please use '
          '"hwid build-database" to prevent from generating legacy pattern.')

    region_field_legacy_info = new_db.region_field_legacy_info
    if not region_field_legacy_info or any(region_field_legacy_info.values()):
      raise common.HWIDException(
          'Legacy region field is forbidden in any new HWID database.')

  @staticmethod
  def VerifyParsedDatabasePattern(old_db, new_db):
    # If the old database follows the new pattern rule, so does the new
    # database.
    if old_db.can_encode and not new_db.can_encode:
      raise common.HWIDException(
          'The new HWID database should not use legacy pattern. '
          'Please use "hwid update-database" to prevent from generating '
          'legacy pattern.')

    # Make sure all the encoded fields in the existing patterns are not changed.
    for image_id in old_db.image_ids:
      old_bit_mapping = old_db.GetBitMapping(image_id=image_id)
      new_bit_mapping = new_db.GetBitMapping(image_id=image_id)
      for index in xrange(len(old_bit_mapping)):
        if new_bit_mapping[index] != old_bit_mapping[index]:
          raise common.HWIDException(
              'Bit pattern mismatch found at bit %d (encoded field=%r). '
              'If you are trying to append new bit(s), be sure to create a new '
              'bit pattern field instead of simply incrementing the last '
              'field' % (index, old_bit_mapping[index][0]))

    old_region_field_legacy_info = old_db.region_field_legacy_info
    new_region_field_legacy_info = new_db.region_field_legacy_info
    for field_name, is_legacy_style in new_region_field_legacy_info.items():
      orig_is_legacy_style = old_region_field_legacy_info.get(field_name)
      if orig_is_legacy_style is None:
        if is_legacy_style:
          raise common.HWIDException(
              'New region field should be constructed by new style yaml tag.')
      else:
        if orig_is_legacy_style != is_legacy_style:
          raise common.HWIDException(
              'Style of existing region field should remain unchanged.')


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--commit', help='the commit to test')
  parser.add_argument('--project', type=str, default=None,
                      help='name of the project to test')
  args = parser.parse_args()
  logging.basicConfig(level=logging.INFO)

  runner = unittest.TextTestRunner()
  test = HWIDDBsPatternTest(project=args.project, commit=args.commit)
  runner.run(test)
