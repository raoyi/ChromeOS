# Copyright 2015 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# TODO(hungte) Remove this legacy file when migration is over.

from __future__ import print_function

import factory_common  # pylint: disable=unused-import
from cros.factory.device import types

DeviceComponent = types.DeviceComponent
DeviceException = types.DeviceException
DeviceProperty = types.DeviceProperty
CalledProcessError = types.CalledProcessError

print('You have imported cros.factory.device.component, which is deprecated by '
      'cros.factory.device.types. Please migrate now.')
