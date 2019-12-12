#!/usr/bin/env python2
# Copyright 2014 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
import unittest

import yaml

import factory_common  # pylint: disable=unused-import
from cros.factory.utils import yaml_utils


class BaseYAMLTagHandlerUnittest(unittest.TestCase):

  def runTest(self):
    class FooTag(object):
      def __init__(self, content):
        self.content = content

    # pylint: disable=unused-variable
    class FooYAMLTagHandler(yaml_utils.BaseYAMLTagHandler):
      YAML_TAG = '!foo'
      TARGET_CLASS = FooTag

      @classmethod
      def YAMLConstructor(cls, loader, node, deep=False):
        value = loader.construct_scalar(node)
        return FooTag(value)

      @classmethod
      def YAMLRepresenter(cls, dumper, data):
        return dumper.represent_scalar(cls.YAML_TAG, data.content)

    # Test load YAML tag.
    value = yaml.load('!foo foo_bar')
    self.assertIsInstance(value, FooTag)
    self.assertEqual('foo_bar', value.content)

    # Test dump YAML tag.
    result = yaml.dump(value)
    self.assertEqual("!foo 'foo_bar'\n", result)


class ParseMappingAsOrderedDictUnittest(unittest.TestCase):
  def setUp(self):
    yaml_utils.ParseMappingAsOrderedDict()

  def tearDown(self):
    yaml_utils.ParseMappingAsOrderedDict(False)

  def testLoadAndDump(self):
    YAML_DOC = '{foo: foo1, bar: 234}'
    obj = yaml.load(YAML_DOC)
    self.assertEqual(obj['foo'], 'foo1')
    self.assertEqual(obj['bar'], 234)
    self.assertEqual(list(obj), ['foo', 'bar'])
    self.assertIsInstance(obj, collections.OrderedDict)

    yaml_str = yaml.dump(obj).strip()
    self.assertEqual(YAML_DOC, yaml_str)

  def testDisable(self):
    YAML_DOC = '{foo: foo1, bar: 234}'
    obj = yaml.load(YAML_DOC)
    self.assertIsInstance(obj, collections.OrderedDict)

    yaml_utils.ParseMappingAsOrderedDict(False)
    obj = yaml.load(YAML_DOC)
    self.assertNotIsInstance(obj, collections.OrderedDict)
    self.assertIsInstance(obj, dict)

  def testModifyDict(self):
    YAML_DOC = '{foo: foo1, bar: 234, buzz: null}'
    EXPECT_YAML_DOC = '{foo: foo1, bar: bar, new_item: new}'
    obj = yaml.load(YAML_DOC)
    obj['bar'] = 'bar'
    obj['new_item'] = 'new'
    del obj['buzz']

    yaml_str = yaml.dump(obj).strip()
    self.assertEqual(EXPECT_YAML_DOC, yaml_str)

if __name__ == '__main__':
  unittest.main()
