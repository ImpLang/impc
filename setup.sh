#!/bin/sh

# go to script directory
a="/$0"; a="${a%/*}"; a="${a:-.}"; a="${a##/}/"; cd "$a";

python3 -m venv venv
. venv/bin/activate

pip install -U pip
pip install -r requirements.txt

ln -svf src/main.py impc
chmod +x impc

printf "\n"
printf "Done. You can now run compiler with ./impc\n"
printf "\n"
printf "If you want to use it system-wide, run following commands:\n"
printf "sudo mkdir -pv /opt/ImpLang\n"
printf "sudo cp -R ./* /opt/ImpLang/\n"
printf "sudo chown -R root:root /opt/ImpLang/\n"
printf "sudo ln -svf /opt/ImpLang/impc /usr/local/bin/impc\n"
