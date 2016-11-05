#!/bin/bash

# for Python 3.4, verified on Ubuntu 14.04
sudo apt-get install python3 python3.4-venv python3-tk libfreetype6-dev
python3 -m venv pyplot
source ./pyplot/bin/activate
pip install matplotlib
cat << EOF > trep.sh
. $PWD/pyplot/bin/activate
python $PWD/trep.py "\$@"
EOF
chmod 755 trep.sh
sudo ln -s $PWD/trep.sh /usr/local/bin/trep
