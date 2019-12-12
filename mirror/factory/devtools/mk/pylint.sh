#!/bin/bash
# Copyright 2016 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
. "${SCRIPT_DIR}/common.sh" || exit 1

: "${PYTHONPATH:=py_pkg:py:setup}"
: "${PYLINT_MSG_TEMPLATE:='{path}:{line}: {symbol}: {msg}'}"
: "${PYLINT_RC_FILE:="${SCRIPT_DIR}/pylint.rc"}"
: "${PYLINT_OPTIONS:=}"
: "${PYLINT_VENV:="${SCRIPT_DIR}/pylint.venv"}"
: "${PYLINT_REQUIREMENTS:="${SCRIPT_DIR}/pylint.requirements.txt"}"

do_lint() {
  local ret="0"
  local out="$1"
  shift
  local num_cpu="$(grep -c ^processor /proc/cpuinfo)"

  PYTHONPATH="${PYTHONPATH}" pylint -j "${num_cpu}" \
    --rcfile="${PYLINT_RC_FILE}" \
    --msg-template="${PYLINT_MSG_TEMPLATE}" \
    ${PYLINT_OPTIONS} \
    "$@" 2>&1 | tee "${out}" || ret="$?"

  if [ "${ret}" != "0" ]; then
    echo
    echo "To re-lint failed files, run:"
    echo " make lint LINT_WHITELIST=\"$(
      grep '^\*' "${out}" | cut -c22- | tr . / | \
      sed 's/$/.py/' | tr '\n' ' ' | sed -e 's/ $//')\""
    echo
    die "Failure in pylint."
  fi
}

load_venv() {
  if ! [ -d "${PYLINT_VENV}" ]; then
    echo "Cannot find '${PYLINT_VENV}', install virtualvenv"
    mkdir -p "${PYLINT_VENV}"
    # Include system site packages for packages like "yaml", "mox".
    virtualenv --system-site-package -p python2 "${PYLINT_VENV}"
  fi

  source "${PYLINT_VENV}/bin/activate"

  if ! diff <(pip freeze --local) "${PYLINT_REQUIREMENTS}" ; then
    pip install -r "${PYLINT_REQUIREMENTS}"
  fi
}

main(){
  set -o pipefail
  local out="$(mktemp)"
  add_temp "${out}"

  load_venv

  echo "Linting $(echo "$@" | wc -w) files..."
  if [ -n "$*" ]; then
    do_lint "${out}" "$@"
  fi
  mk_success
  echo "...no lint errors! You are awesome!"
}

main "$@"
