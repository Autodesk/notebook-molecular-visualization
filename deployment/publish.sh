#!/bin/bash

# Publish a new release (triggered by a git tag that conforms to a PEP440 release)
# Exit 1 if there's a mismatch between the git tag and the package's version
#
# Expects to run in base directory of the repository

# fail immediately if any command fails:
set -e

PKG='nbmolviz'

pyversion=$(python -c "import ${PKG}; print(${PKG}.__version__)" | tail -n 1)

if [[ -z ${CI_BRANCH} ]]; then
  echo "Variable \"\$CI_BRANCH\" not set - cannot publish"
  exit 2
fi

if [ "${pyversion}" == "${CI_BRANCH}" ]; then
  echo "Deploying version ${CI_BRANCH}"
else
  echo "Can't publish - ${PKG} package version '${pyversion}' differs from its Git tag '${CI_BRANCH}'"
  exit 1
fi

echo "Uploading version ${CI_BRANCH} to PyPI:"
twine upload -u ${PYPI_USER} -p ${PYPI_PASSWORD} dist/${PKG}-${pyversion}.tar.gz
