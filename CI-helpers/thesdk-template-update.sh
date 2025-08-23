#!/usr/bin/env bash
#############################################################################
# Update TheSyDeKick thesdk_template with submodule push
# Intended operation: When pushed to the latest release-candidate branch
# Module is automatically updated in thesdk_template and the operation 
# is tested by running the inverter selftest (probably other tests in the future)
# If the tests are passed, the resulting updated thesdk_template module is pushed to
# the latest development branch.
# 
# Written by Marko Kosunen, marko.kosunen@aalto.fi, 18.9.2022
#############################################################################

help_f()
{
cat << EOF    
test_and_release Release 1.0 (18.09.2022)
For testing and releasing TheSyDeKick releases
Written by Marko Pikkis Kosunen

SYNOPSIS
  test_and_release.sh [OPTIONS]
DESCRIPTION
   Defines and runs tests for the submodules of thesdk_template

OPTIONS
  -b 
     Branch of thesdk_template to operate on
     Commit and push to that branch after testing.

  -c Run in CI/CD with this option 

  -t
     STRING : Access token 
  -r
     STRING : Relative path from main project root 
  -h
      Show this help.
EOF
}


# Token we use for push is given as the first argument
CICD="0"
TOKEN=""
BRANCH=""
while getopts b:ct:r:h opt
do
  case "$opt" in
    b) BRANCH="$OPTARG";;
    c) CICD="1";;
    t) TOKEN="$OPTARG";;
    r) RELATIVEPATH="$OPTARG";;
    h) help_f; exit 0;;
    \?) help_f;;
  esac
done

if [ -z "${BRANCH}" ]; then
    echo "Branch not given"
    exit 1
fi

if [ -z "$TOKEN" ] && [ ${CICD} == "1" ]; then
    echo "Token must be provided for CI/CD"
    exit 1
fi

PID="$$"
#Get the current hash
HASH="$(git rev-parse --verify HEAD)"
MESSAGE="$(git log -1 --pretty=%B | head -n 1)"
ROOTDIR=$(pwd)

#Submodule can not know where it is and how it is called
UNDERDEVEL_CANDIDATE="$RELATIVEPATH"

git clone git@github.com:TheSystemDevelopmentKit/thesdk_template.git ./thesdk_template_${PID}
cd ./thesdk_template_${PID}
TEMPLATEDIR="$(pwd)"
WORKDIR="$(pwd)"

# Operate on given branch of thesdk_template
git checkout "$BRANCH"
git pull

#git config --global --add safe.directory /__w/thesdk_template/thesdk_template
#WORKDIR=$(pwd)

PYTHONPATH="$(pwd)/Entities"
export PYTHONPATH

# For local pip-installations to follow the dependencies of the main program
mkdir -p ${HOME}/.local/bin
PATH="${PATH}:${HOME}./local:${HOME}/.local/bin"

# Normal workflow
./configure
# change ssh submodule urls to git
if [ "$CICD" == "1" ]; then
    find ./ -name .gitmodules -exec sed -i 's#\(url = \)\(git@\)\(.*\)\(:\)\(.*$\)#\1https://\3/\5#g' {} \;
fi
#Init the submodules as user would
#Currently fails on ssh cloned subsubmodules
#Must initialize other means
if [ "$CICD" == "1" ]; then
    git submodule update --init 
    find ./ -name .gitmodules -exec sed -i 's#\(url = \)\(git@\)\(.*\)\(:\)\(.*$\)#\1https://\3/\5#g' {} \;
    git submodule update --init --recursive
    find ./ -name .gitmodules -exec sed -i 's#\(url = \)\(git@\)\(.*\)\(:\)\(.*$\)#\1https://\3/\5#g' {} \;
else
    ${WORKDIR}/init_submodules.sh
fi


# Test the dependency installation
# These are already in the buildimage
#./pip3userinstall.sh

SUBMODULES="$(sed -n '/\[submodule/p' .gitmodules | sed -n 's/.* \"\(.*\)\"]/\1/p' | grep "$UNDERDEVEL_CANDIDATE")"
if [ -z "$SUBMODULES" ]; then
    echo "Submodule $UNDERDEVEL_CANDIDATE not found"
    exit 1
else
    echo "Submodule $UNDERDEVEL_CANDIDATE found, proceeding."
fi

cd "${TEMPLATEDIR}/${UNDERDEVEL_CANDIDATE}"
echo "In $(pwd):"
CURRENT="$(git rev-parse HEAD)"
git checkout ${HASH} 2> /dev/null
if [ "$?" == "0" ]; then
    UPDATED="$(git rev-parse HEAD)"
    if [ "${UPDATED}" != "${CURRENT}" ]; then 
        UNDERDEVEL="${UNDERDEVEL_CANDIDATE}"
    fi
else
    echo "Commit ${HASH} does not exist for submodule ${UNDERDEVEL_CANDIDATE}. No changes made."
    exit 0
fi

cd ${ROOTDIR}

cd ${TEMPLATEDIR}
# Let's perform the test(s)
cd ${TEMPLATEDIR}/doc && git remote -v | grep \(fetch\) | sed -n 's#\(.*[://]\)\(.*\)\(\.git.*$\)#\2#p'& make html
DOCSTAT=$?
DOCSTAT="0"

for entity in inverter myentity inverter_tests; do
    cd ${TEMPLATEDIR}/Entities/${entity} && ./configure &&  make sim
    SIMSTAT=$?
    if [ "$SIMSTAT" !=  "0" ] \
        || [ "$DOCSTAT" !=  "0" ]; then
        STATUS="1"
        echo "Tests failed in ${entity}"
        exit 1
    else 
        STATUS="0"
        echo "Tests OK in ${entity}, proceeding"
    fi
done

if [ "$STATUS" == "0" ]; then
    cd ${TEMPLATEDIR}
    for entity in ${UNDERDEVEL}; do 
        echo "Staging $entity"
        git add ${entity}
    done

    echo "Committing changes"
    MSG=""
    COMMITMESSAGE="$(
    cat << EOF
Auto update entities

$(for entity in ${UNDERDEVEL}; do
    echo $entity
done)
EOF
)"
    echo "$COMMITMESSAGE"
    if [ ${CICD} == "1" ]; then 
        git config --global user.name "ecdbot"
        git config --global user.email "${GITHUB_ACTOR}@noreply.github.com"
        git remote set-url origin "https://x-access-token:${TOKEN}@github.com/TheSystemDevelopmentKit/thesdk_template.git"
    fi
    git commit -m"$COMMITMESSAGE"
    #git push
    STATUS=$?
fi
#cd ${WORKDIR} && rm -rf ./thesdk_template_${PID} 
exit $STATUS

