#!/usr/bin/env python2
#
# Copyright 2017 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from __future__ import print_function

import logging
import tempfile
import time
import unittest

import instalog_common  # pylint: disable=unused-import
from instalog import datatypes
from instalog import log_utils
from instalog import plugin_sandbox
from instalog import testing
from instalog.utils import net_utils


class TestPullSocket(unittest.TestCase):

  def setUp(self):
    self.core = testing.MockCore()
    self.hostname = 'localhost'
    self.port = net_utils.FindUnusedPort()

    # Create PluginSandbox for output plugin.
    output_config = {
        'hostname': 'localhost',
        'port': self.port,
        'timeout': 1}
    self.output_sandbox = plugin_sandbox.PluginSandbox(
        'output_pull_socket', config=output_config, core_api=self.core)

    # Create PluginSandbox for input plugin.
    input_config = {
        'hostname': 'localhost',
        'port': self.port}
    self.input_sandbox = plugin_sandbox.PluginSandbox(
        'input_pull_socket', config=input_config, core_api=self.core)

    self.input_sandbox.Start(True)
    self.output_sandbox.Start(True)

    # Store a BufferEventStream.
    self.stream = self.core.GetStream(0)

  def tearDown(self):
    self.input_sandbox.Stop(True)
    self.output_sandbox.Stop(True)
    self.core.Close()

  def testOneEvent(self):
    self.stream.Queue([datatypes.Event({})])
    self.output_sandbox.Flush(2, True)
    time.sleep(0.1)
    self.input_sandbox.Flush(2, True)
    self.assertEqual(self.core.emit_calls, [[datatypes.Event({})]])

  def testOneEventOneAttachment(self):
    with tempfile.NamedTemporaryFile() as f:
      f.write('XXXXXXXXXX')
      f.flush()
      event = datatypes.Event({}, {'my_attachment': f.name})
      self.stream.Queue([event])
      self.output_sandbox.Flush(2, True)
      time.sleep(0.1)
      self.input_sandbox.Flush(2, True)
      self.assertEqual(1, len(self.core.emit_calls))
      event_list = self.core.emit_calls[0]
      self.assertEqual(1, len(event_list))
      self.assertEqual({}, event_list[0].payload)
      self.assertEqual(1, len(event_list[0].attachments))
      self.assertEqual('my_attachment', list(event_list[0].attachments)[0])
      with open(next(iter(event_list[0].attachments.values()))) as f:
        self.assertEqual('XXXXXXXXXX', f.read())


if __name__ == '__main__':
  log_utils.InitLogging(log_utils.GetStreamHandler(logging.INFO))
  unittest.main()
