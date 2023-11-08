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
      install_collection ${collection}
    else
      collection_version=$(echo "${collections_installed}" | awk -F ' ' '{print $2}')
      version="$(grep -v "#" collections.yml | grep -A1 "^  - name: ${collection}" | grep "version: " 2> /dev/null | awk -F ': ' '{print $2}' | sed -e 's|=||' -e 's|>||' -e 's|"||g')"

      echo "The required collection '${collection}' is installed in version ${collection_version}."

      if [ ! -z "${version}" ]
      then

        vercomp "${version}" "${collection_version}"

        case $? in
          0) op='=' ;;
          1) op='>' ;;
          2) op='<' ;;
        esac

        if [[ $op = "=" ]] || [[ $op = ">" ]]
        then
          # echo "FAIL: Expected '$3', Actual '$op', Arg1 '$1', Arg2 '$2'"
          echo "re-install for version ${version}"

          remove_collection ${collection}
          install_collection ${collection}
        else
          :
          # echo "Pass: '$1 $op $2'"
        fi
      else
        :
      fi
    fi
  done
  echo ""
fi

tox ${TOX_OPTS} -- molecule ${TOX_TEST} ${TOX_ARGS}
