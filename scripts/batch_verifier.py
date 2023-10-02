#!/usr/bin/env python3
"""
Examples:
  ./scripts/batch_verifier.py path/to/data/file1.gr path/to/data/file2.gr
  ./scripts/batch_verifier.py --no-color path/to/data 2> logs/result.txt
  ./scripts/batch_verifier.py --solver=dist/buggy-solver --no-color path/to/data 2> logs/result-bug.txt
"""

import sys
import os
import argparse
import subprocess
import multiprocessing

__version__ = '0.0.1'
__license__ = 'Apache License, Version 2.0'


# Path settings.
SCRIPT_PATH = os.path.realpath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
PYTHON_MAIN = os.path.join(PROJECT_DIR, 'src', 'main', 'python')
DEFAULT_SOLVER_DIR = os.path.join(PROJECT_DIR, 'dist')
DEFAULT_SOLVER_PATH = os.path.join(DEFAULT_SOLVER_DIR, 'exact-solver')

if PYTHON_MAIN not in sys.path:
    sys.path.insert(0, PYTHON_MAIN)

from readwrite import load_pace_2023
from util.ColoredLogger import *
from algorithms.common.contraction import verify_contraction_sequence


def get_parser():
    """Argument parser."""

    parser = argparse.ArgumentParser(description='Batch verifier for twin-width solvers.')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('path', nargs='+', help='input file or directory path')
    parser.add_argument('--solver', default=None, help='path to a twin-width solver (default: dist/exact-solver)')
    parser.add_argument('--tww', type=int, default=None, help='expected twin-width')
    parser.add_argument('--log-level', choices=LOG_LEVELS.keys(), default='info', help='log level')
    parser.add_argument('--no-color', action='store_true', help='disables log coloring')
    parser.add_argument('-c', '--cores', default=None, help='number of CPU cores to use')
    return parser


def guess_expected_tww(filename):
    for token in filename.split('_'):
        if token.lower().startswith('tww'):
            return int(token[3:])
    return None


def run_solver(solver_path, input_path):
    proc = subprocess.Popen([solver_path, input_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out = proc.communicate()[0].decode('utf-8')
    return out


def work(data):
    index, total, input_path, solver_path, expected_tww, log_level, no_color = data

    filename = os.path.basename(input_path)
    basename = os.path.splitext(filename)[0]
    log_prefix = f'({index + 1}/{total}) {basename}: '
    logger = get_logger(__name__, log_level, not no_color)

    expected_tww = guess_expected_tww(input_path) if expected_tww is None else expected_tww
    if expected_tww is None:
        logger.error(log_prefix + f'Failed to guess expected tww from filename')
        return

    # run solver
    logger.info(log_prefix + f'Computing (expect={expected_tww})')
    solver_result = run_solver(solver_path, input_path)

    # load graph
    G = load_pace_2023(input_path)

    # verify result
    solver_seq = []
    for line in solver_result.splitlines():
        u, v = map(int, line.strip().split())
        solver_seq += [(u - 1, v - 1)]
    solver_width = verify_contraction_sequence(G, solver_seq)
    if expected_tww != solver_width:
        logger.critical(log_prefix + f'FAILED (expected={expected_tww}, actual={solver_width})')
    else:
        logger.success(log_prefix + f'OK (expected={expected_tww}, actual={solver_width})')


def main(args):
    """Entry point of the program."""

    # logger settings
    log_level = LOG_LEVELS[args.log_level]
    logger = get_logger(__name__, log_level, not args.no_color)

    # get solver path
    solver_path = DEFAULT_SOLVER_PATH if args.solver is None else args.solver
    logger.info(f'Using solver: {solver_path}')

    # collect input files
    paths = []
    for path in args.path:
        if os.path.isdir(path):
            with os.scandir(path) as node:
                for entry in node:
                    if entry.is_file() and entry.name.endswith('.gr'):
                        paths += [entry.path]
        else:
            paths += [path]

    if not paths:
        logger.error('No input files found.')
        return 1

    p = multiprocessing.Pool(args.cores)
    p.map(work, [(i, len(paths), path, solver_path, args.tww, log_level, args.no_color) for i, path in enumerate(paths)])


if __name__ == '__main__':
    main(get_parser().parse_args())
