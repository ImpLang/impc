#!/bin/sh

# go to script directory
a="/$0"; a="${a%/*}"; a="${a:-.}"; a="${a##/}/"; cd "$a";

python3 -m venv venv
. venv/bin/activate

pip install -U pip
pip install -r requirements.txt

ln -svf src/main.py impc
chmod +x impc

echo "\n"
echo "Done. You can now run compiler with ./impc"
echo "\n"
echo "If you want to use it system-wide, run following commands:"
echo "sudo mkdir -pv /opt/ImpLang"
echo "sudo cp -R <project-path>/* /opt/ImpLang/"
echo "sudo chown -R root:root /opt/ImpLang/"
echo "sudo ln -svf /opt/ImpLang/impc /usr/local/bin/impc"
