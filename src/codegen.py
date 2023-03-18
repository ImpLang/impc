from llvmlite import ir

import logger
import parser

def codegen(input_files: list[str], ast: list[parser.Program], output_file: str, verbose: bool = False):
    if verbose:
        logger.compiler_debug("Codegen started")

    llvm_module = ir.Module(name="main")

    # TODO: codegen
