# Nuikta code compilation

**WARNING: The following instructions assume that you are running Linux.**
**Note that Nuikta is not part of the ImpLang project**

To speed up compiler, it is possible to compile the code with Nuikta compiler.
Nuikta is Python to C++ compiler, which is able to convert the ImpLang Compiler
code to binary executable.

See more on [Nuikta project page](https://nuitka.net/)

## Preparation
To correctly compile the code, you need to create virtual environment with
ImplangCompiler dependencies (it is done automatically by `setup.sh` script)
and install Nuikta compiler there.

Assuming you are in the root directory of the project, run the following commands:

```bash
chmod +x setup.sh
./setup.sh
. venv/bin/activate
python -m pip install nuitka
deactivate
```

## Compilation
To compile the code, run the following command:

```bash
. venv/bin/activate # compilation should be done in virtual environment

python -m nuitka --standalone --follow-imports --follow-stdlib --prefer-source-code --lto=yes src/main.py

deactivate
```

## Execution
The compiled code is located in `main.dist` directory. To run it, use the following command:

```bash
./main.dist/main.bin --help
```

## OS-wide installation
To install the compiled code as OS-wide executable, run the following command:

```bash
sudo mkdir -p /opt/ImpLangCompiler/dist
sudo cp -r main.dist/* /opt/ImpLangCompiler/
sudo chown -R root:root /opt/ImpLangCompiler/

sudo ln -sf /opt/ImpLangCompiler/main.bin /usr/local/bin/impc # optional
```
