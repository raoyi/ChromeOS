# Copyright 2017 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import array
import fcntl
import logging
import os
import re
import struct

import factory_common  # pylint: disable=unused-import
from cros.factory.probe import function
from cros.factory.probe.lib import cached_probe_function
from cros.factory.utils import file_utils


def _GetV4L2Data(video_idx):
  # Get information from video4linux2 (v4l2) interface.
  # See /usr/include/linux/videodev2.h for definition of these consts.
  # 'ident' values are defined in include/media/v4l2-chip-ident.h
  info = {}
  VIDIOC_DBG_G_CHIP_IDENT = 0xc02c5651
  V4L2_DBG_CHIP_IDENT_SIZE = 11
  V4L2_INDEX_REVISION = V4L2_DBG_CHIP_IDENT_SIZE - 1
  V4L2_INDEX_IDENT = V4L2_INDEX_REVISION - 1
  V4L2_VALID_IDENT = 3  # V4L2_IDENT_UNKNOWN + 1

  # Get v4l2 capability
  V4L2_CAPABILITY_FORMAT = '<16B32B32BII4I'
  V4L2_CAPABILITY_STRUCT_SIZE = struct.calcsize(V4L2_CAPABILITY_FORMAT)
  V4L2_CAPABILITIES_OFFSET = struct.calcsize(V4L2_CAPABILITY_FORMAT[0:-3])
  # struct v4l2_capability
  # {
  #   __u8  driver[16];
  #   __u8  card[32];
  #   __u8  bus_info[32];
  #   __u32 version;
  #   __u32 capabilities;  /* V4L2_CAPABILITIES_OFFSET */
  #   __u32 reserved[4];
  # };

  IOCTL_VIDIOC_QUERYCAP = 0x80685600

  # Webcam should have CAPTURE capability but no OUTPUT capability.
  V4L2_CAP_VIDEO_CAPTURE = 0x00000001
  V4L2_CAP_VIDEO_OUTPUT = 0x00000002

  # V4L2 encode/decode device should have the following capabilities.
  V4L2_CAP_VIDEO_CAPTURE_MPLANE = 0x00001000
  V4L2_CAP_VIDEO_OUTPUT_MPLANE = 0x00002000
  V4L2_CAP_STREAMING = 0x04000000
  V4L2_CAP_VIDEO_CODEC = (V4L2_CAP_VIDEO_CAPTURE_MPLANE |
                          V4L2_CAP_VIDEO_OUTPUT_MPLANE |
                          V4L2_CAP_STREAMING)

  def _TryIoctl(fileno, request, *args):
    """Try to invoke ioctl without raising an exception if it fails."""
    try:
      fcntl.ioctl(fileno, request, *args)
    except Exception:
      pass

  try:
    with open('/dev/video%d' % video_idx, 'r+') as f:
      # Read chip identifier.
      buf = array.array('i', [0] * V4L2_DBG_CHIP_IDENT_SIZE)
      _TryIoctl(f.fileno(), VIDIOC_DBG_G_CHIP_IDENT, buf, 1)
      v4l2_ident = buf[V4L2_INDEX_IDENT]
      if v4l2_ident >= V4L2_VALID_IDENT:
        info['ident'] = 'V4L2:%04x %04x' % (v4l2_ident,
                                            buf[V4L2_INDEX_REVISION])
      # Read V4L2 capabilities.
      buf = array.array('B', [0] * V4L2_CAPABILITY_STRUCT_SIZE)
      _TryIoctl(f.fileno(), IOCTL_VIDIOC_QUERYCAP, buf, 1)
      capabilities = struct.unpack_from('<I', buf, V4L2_CAPABILITIES_OFFSET)[0]
      if ((capabilities & V4L2_CAP_VIDEO_CAPTURE) and
          (not capabilities & V4L2_CAP_VIDEO_OUTPUT)):
        info['type'] = 'webcam'
      elif capabilities & V4L2_CAP_VIDEO_CODEC == V4L2_CAP_VIDEO_CODEC:
        info['type'] = 'video_codec'
  except Exception:
    pass
  return info


class GenericVideoFunction(cached_probe_function.GlobPathCachedProbeFunction):
  """Probe the generic video information."""

  GLOB_PATH = '/sys/class/video4linux/video*'

  _probed_dev_paths = set()

  @classmethod
  def ProbeDevice(cls, dir_path):
    logging.debug('Find the node: %s', dir_path)

    dev_path = os.path.abspath(os.path.realpath(os.path.join(dir_path,
                                                             'device')))
    if dev_path in cls._probed_dev_paths:
      return None
    cls._probed_dev_paths.add(dev_path)

    result = {}

    results = (
        function.InterpretFunction({'pci': dev_path})() or
        function.InterpretFunction({'usb': os.path.join(dev_path, '..')})())
    assert len(results) <= 1
    if len(results) == 1:
      result.update(results[0])
    else:
      name_path = os.path.join(dir_path, 'name')
      if os.path.exists(name_path):
        device_id = file_utils.ReadFile(name_path)
        if device_id:
          result.update(
              {'name': ' '.join(device_id.replace(chr(0), ' ').split())})

    # TODO(akahuang): Check if these fields are needed.
    # Also check video max packet size
    path = os.path.join(dev_path, 'ep_82', 'wMaxPacketSize')
    if os.path.isfile(path):
      result['wMaxPacketSize'] = file_utils.ReadFile(path).strip()
    # For SOC videos
    path = os.path.join(dev_path, 'control', 'name')
    if os.path.isfile(path):
      result['name'] = file_utils.ReadFile(path).strip()
    # Get video4linux2 (v4l2) result.
    video_idx = re.search(r'video(\d+)$', dir_path).group(1)
    v4l2_data = _GetV4L2Data(int(video_idx))
    if v4l2_data:
      result.update(v4l2_data)

    return result
