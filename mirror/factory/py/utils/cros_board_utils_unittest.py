#!/usr/bin/env python2
# Copyright 2013 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Unit tests for cros_board_utils module."""

import unittest

from six import assertRaisesRegex

import factory_common  # pylint: disable=unused-import
from cros.factory.utils.cros_board_utils import BuildBoard
from cros.factory.utils.cros_board_utils import BuildBoardException


class BuildBoardTest(unittest.TestCase):
  """Unit tests for BuildBoard class."""

  def runTest(self):
    spring = BuildBoard('spring')
    self.assertDictContainsSubset(
        dict(base='daisy', variant='spring', full_name='daisy_spring',
             short_name='spring', gsutil_name='daisy-spring'),
        spring.__dict__)

    # "daisy_spring" and "daisy-spring" should be the same
    for i in ['daisy_spring', 'daisy-spring']:
      self.assertEqual(spring.__dict__, BuildBoard(i).__dict__)

    self.assertDictContainsSubset(
        dict(base='link', variant=None, full_name='link',
             short_name='link', gsutil_name='link'),
        BuildBoard('link').__dict__)

    assertRaisesRegex(
        self, BuildBoardException, 'Unknown board', BuildBoard, 'notarealboard')
    assertRaisesRegex(
        self, BuildBoardException, 'Multiple board names', BuildBoard, 'he')

  def testBoardArch(self):
    self.assertEqual('arm', BuildBoard('beaglebone').arch)
    self.assertEqual('arm', BuildBoard('nyan').arch)
    self.assertEqual('arm', BuildBoard('spring').arch)
    self.assertEqual('amd64', BuildBoard('rambi').arch)
    self.assertEqual('amd64', BuildBoard('link').arch)

if __name__ == '__main__':
  unittest.main()
