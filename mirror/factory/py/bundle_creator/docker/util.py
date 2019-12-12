# Copyright 2017 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


import datetime
import logging
import os
import os.path
import random
import string
import subprocess
import yaml

from six.moves import xrange

from google.cloud import storage  # pylint: disable=import-error, no-name-in-module
from google.protobuf import text_format

import factory_common  # pylint: disable=unused-import
from cros.factory.utils import file_utils
from cros.factory.bundle_creator.docker import config  # pylint: disable=no-name-in-module


class CreateBundleException(Exception):
  pass


def RandomString(length):
  """Returns a randomly generated string of ascii letters.
  Args:
    length: the length for the returned string

  Returns:
    a random ascii letters string
  """
  return ''.join([random.choice(string.ascii_letters) for _ in xrange(length)])


def SetMetadataByGsutil(gs_path, metadata):
  """Set metadata for specified gs_path by using `gsutil` command.

    Args:
      gs_path: the path of google storage object needs to be set metadata
      metadata: a dictionary of metadata should be set
  """
  parameters = []
  for key, value in metadata.items():
    parameters += ['-h'] + ['x-goog-meta-{}:{}'.format(key, value)]
  subprocess.call(['gsutil', 'setmeta'] + parameters + [gs_path])


def CreateBundle(req):
  logger = logging.getLogger('main.createbundle')
  storage_client = storage.Client.from_service_account_json(
      config.SERVICE_ACCOUNT_JSON, project=config.PROJECT)

  logger.info(text_format.MessageToString(req, as_utf8=True, as_one_line=True))

  with file_utils.TempDirectory() as temp_dir:
    os.chdir(temp_dir)
    current_datetime = datetime.datetime.now()
    bundle_name = '{:%Y%m%d}_{}'.format(current_datetime, req.phase)

    firmware_source = ('release_image/' + req.firmware_source
                       if req.HasField('firmware_source')
                       else 'release_image')
    manifest = {
        'board': req.board,
        'project': req.project,
        'bundle_name': bundle_name,
        'toolkit': req.toolkit_version,
        'test_image': req.test_image_version,
        'release_image': req.release_image_version,
        'firmware': firmware_source,
    }
    with open(os.path.join(temp_dir, 'MANIFEST.yaml'), 'w') as f:
      yaml.dump(manifest, f)
    process = subprocess.Popen(
        ['/usr/local/factory/factory.par', 'finalize_bundle',
         os.path.join(temp_dir, 'MANIFEST.yaml')],
        bufsize=1,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    output = ''
    while True:
      line = process.stdout.readline()
      output += line
      if line == '':
        break
      logger.info(line.strip())

    if process.wait() != 0:
      raise CreateBundleException(output)
    bundle_filename = 'factory_bundle_{}_{}.tar.bz2'.format(
        req.project, bundle_name)
    bucket = storage_client.get_bucket(config.BUNDLE_BUCKET)
    blob_filename = 'factory_bundle_{}_{:%Y%m%d_%H%M}_{}_{}.tar.bz2'.format(
        req.project, current_datetime, req.phase, RandomString(6))
    blob_path = '{}/{}/{}'.format(req.board, req.project, blob_filename)
    blob = bucket.blob(blob_path, chunk_size=100 * 1024 * 1024)
    # Set Content-Disposition for the correct default download filename
    blob.content_disposition = 'filename="{}"'.format(blob_filename)
    blob.upload_from_filename(bundle_filename)
    # Set read permission for the email of requestor, entity method here will
    # create a new acl entity and add it to blob.
    blob.acl.entity('user', req.email).grant_read()
    blob.acl.save()

    gs_path = u'gs://{}/{}'.format(config.BUNDLE_BUCKET, blob_path)
    # Since there is no way to modify metadata in blob class, use gsutil command
    # to set metadata
    metadata = {
        'Bundle-Creator': req.email,
        'Tookit-Version': req.toolkit_version,
        'Test-Image-Version': req.test_image_version,
        'Release-Image-Version': req.release_image_version,
    }
    if req.HasField('firmware_source'):
      metadata['Firmware-Source'] = req.firmware_source
    SetMetadataByGsutil(gs_path, metadata)
    return gs_path
