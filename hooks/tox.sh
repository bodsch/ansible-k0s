#!/usr/bin/env bash

. hooks/molecule.rc

TOX_TEST="${1}"

if [ -f "./collections.yml" ]
then
  for collection in $(grep -v "#" collections.yml | grep "^  - name: " | awk -F ': ' '{print $2}')
  do
    collections_installed="$(ansible-galaxy collection list | grep ${collection} 2> /dev/null)"

    if [ -z "${collections_installed}" ]
    then
      echo "Install the required collection '${collection}'"
      ansible-galaxy collection install ${collection}
    else
      collection_version=$(echo "${collections_installed}" | awk -F ' ' '{print $2}')

      echo "The required collection '${collection}' is installed in version ${collection_version}."
    fi
  done
  echo ""
fi

tox ${TOX_OPTS} -- molecule ${TOX_TEST} ${TOX_ARGS}
