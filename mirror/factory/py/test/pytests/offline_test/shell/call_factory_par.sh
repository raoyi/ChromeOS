#!/bin/sh
# Copyright 2016 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

task_{%id%} () {
  CROS_FACTORY_TEST_PATH={%pytest_name%} {%cmd%}
  return "$?"
}
