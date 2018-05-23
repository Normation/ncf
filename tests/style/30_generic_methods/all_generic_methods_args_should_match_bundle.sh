#!/bin/sh

#####################################################################################
# Copyright 2018 Normation SAS
#####################################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, Version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#####################################################################################
set -e

# Check that all generic_methods which have an args variable to check if it matches the bundle's arguments

FILES_TO_CHECK=`find "${NCF_TREE}/30_generic_methods/" -name "*.cf"`
NB_ERROR=0
for f in ${FILES_TO_CHECK}
do
  ARGS=$(grep -E "\"args\"\s+slist" $f | grep -Eo '\{\s*(.*)\s*\}' | sed "s/[{}\"\$ ]//g") && true
  
  if [ "$ARGS" != "" ]; then
    # File has an args variable
    BUNDLE_ARGS=$(grep -E "bundle agent" $f | grep -Eo '(\(.*\))' | sed "s/[() ]//g" )
    if [ "$ARGS" != "$BUNDLE_ARGS" ]; then
      echo "File $f has wrong args variable"
      NB_ERROR=`expr $NB_ERROR + 1`
    fi
  fi
done

if [ $NB_ERROR -eq 0 ]; then
  echo "R: $0 Pass"
else
  echo "R: $0 FAIL"
fi

exit $NB_ERROR
