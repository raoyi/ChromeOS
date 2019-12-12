// Copyright 2018 The Chromium OS Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import {RootState} from '@app/types';

import {displayedState} from '@common/optimistic_update';

import {NAME} from './constants';
import {ConfigState} from './reducer';

export const localState = (state: RootState): ConfigState =>
  displayedState(state)[NAME];

export const isTftpEnabled =
  (state: RootState): boolean => localState(state).config.tftpEnabled;
export const isConfigUpdating =
  (state: RootState): boolean => localState(state).updating;
