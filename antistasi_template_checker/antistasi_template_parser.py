"""
[summary]

[extended_summary]
"""

# region [Imports]

# * Standard Library Imports ------------------------------------------------------------------------------------------------------------------------------------>

import gc
import os
import re
import sys
import json
import lzma
import time
import queue
import base64
import pickle
import random
import shelve
import shutil
import asyncio
import logging
import sqlite3
import platform
import importlib
import subprocess
import unicodedata

from io import BytesIO
from abc import ABC, abstractmethod
from copy import copy, deepcopy
from enum import Enum, Flag, auto
from time import time, sleep
from pprint import pprint, pformat
from string import Formatter, digits, printable, whitespace, punctuation, ascii_letters, ascii_lowercase, ascii_uppercase
from timeit import Timer
from typing import Union, Callable, Iterable
from inspect import stack, getdoc, getmodule, getsource, getmembers, getmodulename, getsourcefile, getfullargspec, getsourcelines
from zipfile import ZipFile
from datetime import tzinfo, datetime, timezone, timedelta
from tempfile import TemporaryDirectory, TemporaryFile
from textwrap import TextWrapper, fill, wrap, dedent, indent, shorten
from functools import wraps, partial, lru_cache, singledispatch, total_ordering, reduce
from importlib import import_module, invalidate_caches
from contextlib import contextmanager
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from urllib.parse import urlparse
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from importlib.machinery import SourceFileLoader
from itertools import chain

# * Third Party Imports ----------------------------------------------------------------------------------------------------------------------------------------->


from natsort import natsorted, IGNORECASE, LOCALE


from fuzzywuzzy import fuzz, process as fuzzprocess

from pyparsing import nestedExpr
from .data.identifiers import IDENTIFIERS
from .data.name_list import NAME_LIST

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [AppUserData]


# endregion [AppUserData]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = os.path.abspath(os.path.dirname(__file__))


# endregion[Constants]


# region [Helper]
def pathmaker(first_segment, *in_path_segments, rev=False):
    """
    Normalizes input path or path fragments, replaces '\\\\' with '/' and combines fragments.

    Parameters
    ----------
    first_segment : str
        first path segment, if it is 'cwd' gets replaced by 'os.getcwd()'
    rev : bool, optional
        If 'True' reverts path back to Windows default, by default None

    Returns
    -------
    str
        New path from segments and normalized.
    """

    _path = first_segment

    _path = os.path.join(_path, *in_path_segments)
    if rev is True or sys.platform not in ['win32', 'linux']:
        return os.path.normpath(_path)
    return os.path.normpath(_path).replace(os.path.sep, '/')


def loadjson(in_file):
    with open(in_file, 'r') as jsonfile:
        _out = json.load(jsonfile)
    return _out


def writejson(in_object, in_file, sort_keys=True, indent=4):
    with open(in_file, 'w') as jsonoutfile:
        json.dump(in_object, jsonoutfile, sort_keys=sort_keys, indent=indent)


def readit(in_file, per_lines=False, in_encoding='utf-8', in_errors=None):
    """
    Reads a file.

    Parameters
    ----------
    in_file : str
        A file path
    per_lines : bool, optional
        If True, returns a list of all lines, by default False
    in_encoding : str, optional
        Sets the encoding, by default 'utf-8'
    in_errors : str, optional
        How to handle encoding errors, either 'strict' or 'ignore', by default 'strict'

    Returns
    -------
    str/list
        the read in file as string or list (if per_lines is True)
    """
    with open(in_file, 'r', encoding=in_encoding, errors=in_errors) as _rfile:
        _content = _rfile.read()
    if per_lines is True:
        _content = _content.splitlines()

    return _content


# endregion [Helper]

TEMPLATE_FILE = r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\Arma_class_parser_utility\temp\antistasi_templates\RHS_AI_USAF_Marines_Arid.sqf"


square_bracket_regex = re.compile(r"^.*?(?P<square_bracket_part>\[.*)")
quoted_regex = re.compile(r'".*?"')

identifiers = set(loadjson(pathmaker(THIS_FILE_DIR, 'identifiers.json')))
json_folder = pathmaker(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\Arma_class_parser_utility\temp\temp_output")


def split_file(in_file):
    content = readit(in_file)
    writeit('split_off_side_information_vehicles.sqf', content.split('//       Loadouts       //')[0])


def clean_comments(line):
    return line.split('//')[0]


def get_line(in_file):
    for index, _line in enumerate(readit(in_file).splitlines()):
        _line = _line.split('//')[0]
        _line = _line.split(' call')[0]
        if _line != '' and '[' in _line:
            yield index, _line


def get_token_between_chars(string, start_char, end_char, level=0, out_dict=None):
    if level == 0:
        result_dict = {}
    else:
        result_dict = out_dict
    token = ''

    n_left = 0
    n_right = 0
    closed = False

    start_index = 0
    end_index = 0
    count = 0
    string = ''.join(string.splitlines()).strip().replace('\t', '').replace('/s', '').strip()
    for c in string:
        if c == start_char:
            n_left += 1
            if n_left == 1:
                start_index = count
        elif c == end_char:
            n_right += 1

        if n_left > n_right and not closed:
            token += c
        elif n_left > 0 and n_left == n_right:
            closed = True
            end_index = count
            break

        count += 1

    token = token[1: len(token)].lstrip("[").rstrip(']')
    if token:
        result_dict[level] = []
        token = token.strip()
        for item in token.split(','):
            item.strip().replace('\t', '').replace('\n', '').replace('\n[', '').strip()
            item = item.strip().replace('[', '').replace(']', '').replace('"', '').strip()
            if item:
                result_dict[level].append(item)
    if '[' in token:
        return get_token_between_chars(token, "[", ']', level + 1, result_dict)
    return result_dict


def is_integer(item):
    try:
        x = int(item)
        return True
    except ValueError:
        return False


def filter_token_dict(line):
    token_dict = get_token_between_chars(line, '[', ']')
    amount_keys = len(token_dict) - 1
    for i in range(amount_keys):
        if i != amount_keys:
            token_dict[i] = list(set(token_dict[i]) - set(token_dict[i + 1]))
    return token_dict


def all_item_jsons():
    for json_file in os.scandir(pathmaker(THIS_FILE_DIR, "jsons")):
        if json_file.is_file() is True:
            if json_file.name.endswith('_item_names.json'):
                yield loadjson(json_file.path)


def check_item(item):
    for name_list in all_item_jsons():
        if item in name_list:
            return True
    return False


def get_possible_correction(item):
    name_list = []
    for json_data in all_item_jsons():
        name_list += json_data
    if os.path.isfile(pathmaker(THIS_FILE_DIR, 'jsons', 'full_name_list.json')) is False:
        writejson(name_list, pathmaker(THIS_FILE_DIR, 'jsons', 'full_name_list.json'))
    result = fuzzprocess.extractOne(item, name_list, scorer=fuzz.token_sort_ratio)
    if result is not None:
        return result[0]
    return None


def get_content(in_file):
    for index, _line in get_line(in_file):
        _content = filter_token_dict(_line)
        yield index, _content


def get_items(in_file):

    _identifiers = []
    for index, content in get_content(in_file):
        for level, items in content.items():
            for item in items:
                if item not in identifiers and check_item(item) is False and is_integer(item) is False:
                    possible_correction = get_possible_correction(item)
                    yield index, item, possible_correction


def run(in_file):
    dir_name = os.path.dirname(in_file)
    raw_filename = os.path.splitext(os.path.basename(in_file))[0]
    out_file = pathmaker(dir_name, f"{raw_filename}_errors.txt")
    for _index, x_item, pos_correct in get_items(TEMPLATE_FILE):
        with open(out_file, 'w') as out_f:
            if '\\' in x_item:
                text = f"is this maybe an file path? -> {x_item} in line {str(_index)}"
            else:
                if pos_correct is None:
                    text = f'line: {str(_index)} -> "{x_item}", NO POSSIBLE CORRECTION FOUND'
                else:
                    text = f'line: {str(_index)} -> "{x_item}", did you maybe mean "{pos_correct}"'
            print(text)

            out_f.write(text + '\n')

# region[Main_Exec]


if __name__ == '__main__':

    in_file = sys.argv[1]
    if os.path.exists(in_file) is False:
        raise FileNotFoundError(in_file)
    if os.path.isfile(in_file) is False:
        raise FileNotFoundError(in_file)
    run(in_file)

# endregion[Main_Exec]
