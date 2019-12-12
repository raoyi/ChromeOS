#!/bin/bash
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

DEPLOY_DIR="$(dirname "$(readlink -f "$0")")"
FACTORY_DIR="$(readlink -f "${DEPLOY_DIR}/..")"
APPENGINE_DIR="${FACTORY_DIR}/py/hwid/service/appengine"
HW_VERIFIER_DIR="${FACTORY_DIR}/../../platform2/hardware_verifier"
RT_PROBE_DIR="${FACTORY_DIR}/../../platform2/system_api/dbus/runtime_probe"
TEST_DIR="${APPENGINE_DIR}/test"
PLATFORM_DIR="$(dirname ${FACTORY_DIR})"
REGIONS_DIR="$(readlink -f "${FACTORY_DIR}/../../platform2/regions")"
TEMP_DIR="${FACTORY_DIR}/build/hwid"
ENV_PROD="chromeos-hwid"
ENV_STAGING="chromeos-hwid-staging"
ENV_LOCAL="LOCAL"
ENDPOINTS_SUFFIX=".appspot.com"

. "${FACTORY_DIR}/devtools/mk/common.sh" || exit 1

check_docker() {
  if ! type docker >/dev/null 2>&1; then
    die "Docker not installed, abort."
  fi
  DOCKER="docker"
  if [ "$(id -un)" != "root" ]; then
    if ! echo "begin $(id -Gn) end" | grep -q " docker "; then
      echo "You are neither root nor in the docker group,"
      echo "so you'll be asked for root permission..."
      DOCKER="sudo docker"
    fi
  fi

  # Check Docker version
  local docker_version="$(${DOCKER} version --format '{{.Server.Version}}' \
                          2>/dev/null)"
  if [ -z "${docker_version}" ]; then
    # Old Docker (i.e., 1.6.2) does not support --format.
    docker_version="$(${DOCKER} version | sed -n 's/Server version: //p')"
  fi
  local error_message=""
  error_message+="Require Docker version >= ${DOCKER_VERSION} but you have "
  error_message+="${docker_version}"
  local required_version=(${DOCKER_VERSION//./ })
  local current_version=(${docker_version//./ })
  for ((i = 0; i < ${#required_version[@]}; ++i)); do
    if (( ${#current_version[@]} <= i )); then
      die "${error_message}"  # the current version array is not long enough
    elif (( ${required_version[$i]} < ${current_version[$i]} )); then
      break
    elif (( ${required_version[$i]} > ${current_version[$i]} )); then
      die "${error_message}"
    fi
  done
}

check_gcloud() {
  if ! type gcloud >/dev/null 2>&1; then
    die "Cannot find gcloud, please install gcloud first"
  fi
}

check_credentials() {
  check_gcloud

  ids="$(gcloud auth list --filter=status:ACTIVE --format="value(account)")"
  for id in ${ids}; do
    if [[ "${id}" =~ .*"@google.com" ]]; then
      return 0
    fi
  done
  project="$1"
  gcloud auth application-default --project "${project}" login
}

run_in_temp() {
  (cd "${TEMP_DIR}"; "$@")
}

prepare_cros_regions() {
  cros_regions="${TEMP_DIR}/cros-regions.json"
  ${REGIONS_DIR}/regions.py --format=json --all --notes > "${cros_regions}"
  add_temp "${cros_regions}"
}

prepare_protobuf() {
  local protobuf_out="${TEMP_DIR}/protobuf_out"
  mkdir -p "${protobuf_out}"
  protoc \
    -I="${RT_PROBE_DIR}" \
    -I="${HW_VERIFIER_DIR}" \
    --python_out="${protobuf_out}" \
    "${HW_VERIFIER_DIR}/hardware_verifier.proto" \
    "${RT_PROBE_DIR}/runtime_probe.proto"
}

get_latest_endpoint_config_version() {
  local service_name="$1${ENDPOINTS_SUFFIX}"
  gcloud endpoints configs list --service="${service_name}" --limit=1 \
    | tail -n1 | cut -f1 -d' '
}

do_deploy() {
  gcp_project="$1"
  shift
  check_gcloud
  check_credentials "${gcp_project}"

  if [ "${gcp_project}" == "${ENV_PROD}" ]; then
    do_test
  fi

  mkdir -p "${TEMP_DIR}/lib"
  SYMLINK_FILES=(app.yaml cron.yaml appengine_config.py requirements.txt)
  for file in "${SYMLINK_FILES[@]}"; do
    ln -fs "${APPENGINE_DIR}/${file}" "${TEMP_DIR}"
  done
  ln -fs "${FACTORY_DIR}/py_pkg/cros" "${TEMP_DIR}"
  ln -fs "${FACTORY_DIR}/py_pkg/cros/factory/factory_common.py" "${TEMP_DIR}"

  prepare_protobuf
  prepare_cros_regions
  run_in_temp virtualenv env
  source "${TEMP_DIR}/env/bin/activate"
  add_temp "${TEMP_DIR}/env"
  run_in_temp \
    pip install -t lib -r requirements.txt
  deactivate
  if [ "${gcp_project}" != "${ENV_LOCAL}" ]; then
    endpoints_version="$(get_latest_endpoint_config_version "${gcp_project}")"
    run_in_temp cat << __EOF__ > "${TEMP_DIR}/env.yaml"
env_variables:
  ENDPOINTS_SERVICE_VERSION: ${endpoints_version}
  ENDPOINTS_SERVICE_NAME: ${gcp_project}${ENDPOINTS_SUFFIX}
__EOF__
    run_in_temp gcloud --project="${gcp_project}" app deploy app.yaml cron.yaml
  else
    # Create an empty env.yaml
    run_in_temp echo -n > "${TEMP_DIR}/env.yaml"
    run_in_temp dev_appserver.py "${@}" app.yaml
  fi
}

do_build() {
  check_docker

  local dockerfile="${TEST_DIR}/Dockerfile"
  ignore_list+="*\n"
  ignore_list+="!factory\n"
  ignore_list+="!chromeos-hwid\n"
  ignore_list+="factory/build/*\n"
  ignore_list+="!factory/build/hwid/protobuf_out\n"
  local dockerignore="${PLATFORM_DIR}"/.dockerignore
  add_temp "${dockerignore}"
  echo -e "${ignore_list}" > "${dockerignore}"
  prepare_protobuf

  ${DOCKER} build \
    --file "${dockerfile}" \
    --tag "appengine_integration" \
    "${PLATFORM_DIR}"
}

do_test() {
  # Runs all executables in the test folder.
  for test_exec in $(find "${TEST_DIR}" -executable -type f); do
    echo Running "${test_exec}"
    "${test_exec}"
  done
}

usage() {
  cat << __EOF__
Chrome OS HWID Service Deployment Script

commands:
  $0 help
      Shows this help message.
      More about HWIDService: go/factory-git/py/hwid/service/appengine/README.md

  $0 deploy [prod|staging]
      Deploys HWID Service to the given environment by gcloud command.

  $0 deploy local [args...]
      Deploys HWID Service locally via dep_appserver.py tool.  Arguments will
      be delegated to the tool.

  $0 build
      Builds docker image for AppEngine integration test.

  $0 test
      Runs all executables in the test directory.

__EOF__
}

main() {
  local proejct=""
  case "$1" in
    deploy)
      shift
      [ $# -gt 0 ] || (usage && exit 1);
      case "$1" in
        prod)
          project="${ENV_PROD}"
          ;;
        staging)
          project="${ENV_STAGING}"
          ;;
        local)
          project="${ENV_LOCAL}"
          ;;
        *)
          usage && exit 1
      esac
      shift
      do_deploy "${project}" "${@}"
       ;;
    build)
      do_build
      ;;
    test)
      do_test
      ;;
    *)
      usage
      exit 1
      ;;
  esac

  mk_success
}

main "$@"
