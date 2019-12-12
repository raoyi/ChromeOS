#!/usr/bin/env python2
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
import unittest

import factory_common  # pylint: disable=unused-import
from cros.factory.hwid.v3 import rule
from cros.factory.hwid.v3 import yaml_wrapper as yaml
from cros.factory.test.l10n import regions


_REGIONS_DATABASE_PATH = os.path.join(
    os.path.dirname(__file__), 'testdata', 'test_yaml_wrapper_regions.json')


class ParseRegionFieldUnittest(unittest.TestCase):
  def testDecodeYAMLTag(self):
    doc = 'foo: !region_field'
    decoded = yaml.load(doc)
    self.assertEqual({'region': 'us'}, decoded['foo'][29])
    self.assertEqual({'region': 'sa'}, decoded['foo'][128])
    self.assertFalse(127 in decoded['foo'])  # region 'zw' is not confirmed yet.
    self.assertTrue(decoded['foo'].is_legacy_style)

    # "no" should not be parsed as "false" (boolean) here.
    doc = 'foo: !region_field [us, gb, no]'
    decoded = yaml.load(doc)
    self.assertFalse(decoded['foo'].is_legacy_style)
    self.assertEqual(decoded['foo'], {
        0: {'region': []},
        1: {'region': 'us'},
        2: {'region': 'gb'},
        3: {'region': 'no'}})

  def testDumpRegionField(self):
    doc = 'foo: !region_field [us, gb]'
    decoded = yaml.load(doc)
    dump_str = yaml.dump(decoded).strip()
    self.assertEqual(doc, dump_str)

    doc = 'foo: !region_field'
    decoded = yaml.load(doc)
    dump_str = yaml.dump(decoded, default_flow_style=False).strip()
    self.assertEqual(doc, dump_str)


class ParseRegionComponentUnittest(unittest.TestCase):
  def setUp(self):
    regions.InitialSetup(
        region_database_path=_REGIONS_DATABASE_PATH, include_all=False)

  def tearDown(self):
    regions.InitialSetup()

  def testLoadRegionComponent(self):
    for s in ('region: !region_component', 'region: !region_component {}'):
      obj = yaml.load(s)['region']
      self.assertEqual(dict(obj), {
          'items': {
              'aa': {'values': {'region_code': 'aa'}},
              'bb': {'values': {'region_code': 'bb'}},
              'zz': {'values': {'region_code': 'zz'},
                     'status': 'unsupported'}}})

  def testLoadRegionComponentStatusLists(self):
    obj = yaml.load('region: !region_component\n'
                    '  unqualified: [aa]\n'
                    '  deprecated: [zz]\n')['region']
    self.assertEqual(dict(obj), {
        'items': {
            'aa': {'values': {'region_code': 'aa'},
                   'status': 'unqualified'},
            'bb': {'values': {'region_code': 'bb'}},
            'zz': {'values': {'region_code': 'zz'},
                   'status': 'deprecated'}}})

  def testLoadRegionComponentError(self):
    self.assertRaises(Exception, yaml.load, 'region: !region_component 123')
    self.assertRaises(Exception, yaml.load,
                      'region: !region_component\n'
                      '  bad_key: []\n')
    self.assertRaises(Exception, yaml.load,
                      'region: !region_component\n'
                      '  unqualified: tw\n')
    self.assertRaises(Exception, yaml.load,
                      'region: !region_component\n'
                      '  unqualified: []\n')
    self.assertRaises(Exception, yaml.load,
                      'region: !region_component\n'
                      '  unqualified: [tw, us]\n'
                      '  deprecated: [us, gb]\n')

  def testDumpRegionComponent(self):
    load2 = lambda doc: yaml.load(yaml.dump(yaml.load(doc),
                                            default_flow_style=False))
    doc = 'region: !region_component\n'
    self.assertEqual(yaml.load(doc), load2(doc))
    doc = 'region: !region_component {}\n'
    self.assertEqual(yaml.load(doc), load2(doc))

    doc = 'region: !region_component\n  unqualified: [zz]\n'
    self.assertEqual(yaml.load(doc), load2(doc))
    doc = 'region: !region_component\n  unqualified: [zz]\n  unsupported: [aa]'
    self.assertEqual(yaml.load(doc), load2(doc))


class StandardizeUnittest(unittest.TestCase):
  def testParseBool(self):
    self.assertEqual(yaml.load('true'), True)
    self.assertEqual(yaml.load('TRUE'), True)
    self.assertEqual(yaml.load('false'), False)
    self.assertEqual(yaml.load('FALSE'), False)

    self.assertEqual(yaml.load('no'), 'no')
    self.assertEqual(yaml.load('NO'), 'NO')
    self.assertEqual(yaml.load('yes'), 'yes')
    self.assertEqual(yaml.load('YES'), 'YES')

    self.assertEqual(yaml.load('on'), 'on')
    self.assertEqual(yaml.load('ON'), 'ON')
    self.assertEqual(yaml.load('off'), 'off')
    self.assertEqual(yaml.load('OFF'), 'OFF')


@rule.RuleFunction(['string'])
def StrLen():
  return len(rule.GetContext().string)


@rule.RuleFunction(['string'])
def AssertStrLen(length):
  logger = rule.GetLogger()
  if len(rule.GetContext().string) <= length:
    logger.Error('Assertion error')


class ValueYAMLTagTest(unittest.TestCase):
  def testYAMLParsing(self):
    self.assertEqual(yaml.load('!re abc'), rule.Value('abc', is_re=True))
    self.assertEqual(yaml.load(yaml.dump(rule.Value('abc', is_re=False))),
                     'abc')
    self.assertEqual(yaml.dump(rule.Value('abc', is_re=True)), "!re 'abc'\n")


if __name__ == '__main__':
  unittest.main()
