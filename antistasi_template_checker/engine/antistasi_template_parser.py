
"""
[summary]

"""
# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import re
import sys
import json

# * Third Party Imports --------------------------------------------------------------------------------->
from fuzzywuzzy import fuzz
from fuzzywuzzy import process as fuzzprocess

# * Local Imports --------------------------------------------------------------------------------------->
from antistasi_template_checker.data.name_list import NAME_LIST
from antistasi_template_checker.data.identifiers import IDENTIFIERS
from antistasi_template_checker.utility.named_tuples import TemplateItem

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [AppUserData]


# endregion [AppUserData]

# region [Logging]


# endregion[Logging]

# region [Constants]


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


square_bracket_regex = re.compile(r"^.*?(?P<square_bracket_part>\[.*)")
quoted_regex = re.compile(r'".*?"')


json_folder = pathmaker(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\Arma_class_parser_utility\temp\temp_output")
REPORT_SPACING_1 = 10
REPORT_SPACING_2 = 40
NAME_LIST_CASEFOLDED = set(list(map(lambda x: x.casefold(), NAME_LIST)))


def clean_comments(line):
    return line.split('//')[0]


def get_line(in_data):
    for index, _line in enumerate(in_data.splitlines()):
        _line = _line.split('//')[0]
        _line = _line.split(' call')[0]
        if _line != '' and '[' in _line and not _line.startswith('["spawnMarkerName",') and not _line.startswith('["name",'):
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


def check_item(item, case_insensitive):
    if case_insensitive is True:
        item = item.casefold()
        _name_list = NAME_LIST_CASEFOLDED
    else:
        _name_list = NAME_LIST
    if item in _name_list or item == ';':
        return True
    return False


def get_possible_correction(item):
    result = fuzzprocess.extractOne(item, NAME_LIST, scorer=fuzz.token_sort_ratio)
    if result is not None:
        return result[0]
    return None


def get_content(in_data):
    for index, _line in get_line(in_data):
        _content = filter_token_dict(_line)
        yield index, _content


def check_identifier(item):
    if item in IDENTIFIERS:
        return True
    elif "Support Corridor" in item:
        return True
    return any(item.startswith(prefix) for prefix in IDENTIFIERS)


def get_items(in_data, case_insensitive):

    for index, content in get_content(in_data):
        for level, items in content.items():
            for item in items:
                possible_correction = None
                has_error = False
                is_case_error = False
                if check_item(item, case_insensitive) is False and is_integer(item) is False and check_identifier(item) is False:
                    if '\\' in item:
                        possible_correction = 'FILEPATH'
                    else:
                        possible_correction = get_possible_correction(item)
                    if possible_correction is None:
                        possible_correction = 'NO CORRECTION FOUND'
                    has_error = True
                    is_case_error = True if item.casefold() == possible_correction.casefold() else False
                yield TemplateItem(item=item, line_number=index + 1, has_error=has_error, correction=possible_correction, is_case_error=is_case_error)


def run(in_data: str, case_insensitive=False):

    _out = {'found_errors': 0, 'items': []}

    for template_item in get_items(in_data, case_insensitive):
        if template_item.has_error is True:
            _out['found_errors'] += 1
        _out['items'].append(template_item)
    return _out
# region[Main_Exec]


if __name__ == '__main__':
    pass
# endregion[Main_Exec]
