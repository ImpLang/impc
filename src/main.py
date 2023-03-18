#!/usr/bin/env python3

# The ImpLang programming language compiler
# Made by: HXM4Tech

import argparse
import os
import sys
import signal
import traceback

import logger # pre-import to enable logging before entering the virtual environment

def on_sigint(signal, frame):
    logger.compiler_info("Received SIGINT, exiting...")
    exit(2)

if __name__ == "__main__":
    # Activate the virtual environment
    venv_path = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "venv"))

    if os.path.isdir(venv_path):
        sys.path.insert(0, os.path.join(venv_path, "bin"))
        sys.path.insert(0, os.path.join(venv_path, "lib", f"python{sys.version_info.major}.{sys.version_info.minor}", "site-packages"))
    else:
        logger.compiler_error("Virtual environment not found!")
        logger.compiler_info("Please run the 'setup.sh' script to create the virtual environment")
        exit(1)

    # disable bytecode generation
    sys.dont_write_bytecode = True

    # setup SIGINT handler
    signal.signal(signal.SIGINT, on_sigint)

import defs
import logger
import lexer
import parser

def main():
    arg_parser = argparse.ArgumentParser(description=f"{defs.COMPILER_NAME} v{defs.COMPILER_VERSION}")

    arg_parser.add_argument("input", help="The input file(s) to compile", nargs="*")
    arg_parser.add_argument("-o", "--output", help="The output file to write to", default="a.out")
    arg_parser.add_argument("-c", "--compile-only", help="Only compile the input file, do not link", action="store_true")
    arg_parser.add_argument("-S", "--assembly", help="Compile the input file to assembly", action="store_true")
    arg_parser.add_argument("-v", "--verbose", help="Enable verbose output", action="store_true")
    arg_parser.add_argument("-V", "--version", help="Print the compiler version", action="store_true")
    
    args = arg_parser.parse_args()

    if args.version:
        print(f"{defs.COMPILER_NAME} v{defs.COMPILER_VERSION}")
        exit(0)
    else:
        if not args.input:
            logger.compiler_error("No input files specified")
            exit(1)

    if args.verbose:
        logger.compiler_debug(f"Verbose output enabled")

    args.input = [os.path.abspath(input_file) for input_file in args.input]

    for input_file in args.input:
        if not os.path.isfile(input_file):
            logger.compiler_error(f"Input file '{input_file}' does not exist")
            exit(1)

        if not os.access(input_file, os.R_OK):
            logger.compiler_error(f"Input file '{input_file}' is not readable")
            logger.compiler_info(f"Make sure that you have the correct permissions to read the file")
            exit(1)

    args.output = os.path.abspath(args.output)

    if os.path.isfile(args.output):
        if not os.access(args.output, os.W_OK):
            logger.compiler_error(f"Output file '{args.output}' is not writable")
            logger.compiler_info(f"Make sure that you have the correct permissions to write to the file")
            exit(1)
        
        logger.compiler_warning(f"Output file '{args.output}' already exists and will be overwritten")
    else:
        if os.path.exists(os.path.dirname(args.output)):
            if not os.access(os.path.dirname(args.output), os.W_OK):
                logger.compiler_error(f"Output file '{args.output}' does not exist and cannot be created")
                logger.compiler_info(f"Make sure that you have the correct permissions to write to the parent directory")
                exit(1)
        else:
            logger.compiler_error(f"Output file '{args.output}' does not exist and cannot be created (parent directory does not exist))")
            exit(1)

    # check if the output file is a directory
    if os.path.isdir(args.output):
        logger.compiler_error(f"Output file '{args.output}' is a directory")
        exit(1)

    if args.verbose:
        logger.compiler_debug("Arguments:")
        logger.compiler_debug(f"Input file(s): {args.input}")
        logger.compiler_debug(f"Output file: {args.output}")
        logger.compiler_debug(f"Compile only: {args.compile_only}")
        logger.compiler_debug(f"Assembly: {args.assembly}")
        logger.compiler_debug(f"Verbose: {args.verbose}")

    lexer_output = {}

    for input_file in args.input:
        lexer_output[input_file] = lexer.lex_file(input_file)

    if args.verbose:
        logger.compiler_debug("Lexer output:")
        logger.compiler_debug(lexer_output)

    parser_output = {}

    for f_name, tokens in lexer_output.items():
        parser_output[f_name] = parser.parse(f_name, tokens)

    if args.verbose:
        logger.compiler_debug("Parser output:")
        logger.compiler_debug(parser_output)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.cut_here()
        logger.compiler_error(f"An unhandled exception occurred!")

        tb = traceback.format_exc().splitlines()
        for x in [2, 1]: tb.pop(x)

        for line in tb:
            logger.compiler_error(line)

        print(file=sys.stderr)
        logger.compiler_info("Please report this error in the GitHub issue")

        exit(1)
