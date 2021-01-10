

# region [Imports]

# * Standard Library Imports ------------------------------------------------------------------------------------------------------------------------------------>

import os
import re
import sys
import json


from fuzzywuzzy import fuzz, process as fuzzprocess

from antistasi_template_checker.data.general_data import IDENTIFIERS, JSON_COMBINED_NAME_LIST

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


def clean_comments(line):
    return line.split('//')[0]


def get_line(in_file):
    for index, _line in enumerate(readit(in_file).splitlines()):
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


def check_item(item):

    if item in JSON_COMBINED_NAME_LIST:
        return True
    return False


def get_possible_correction(item):
    result = fuzzprocess.extractOne(item, JSON_COMBINED_NAME_LIST, scorer=fuzz.token_sort_ratio)
    if result is not None:
        return result[0]
    return None


def get_content(in_file):
    for index, _line in get_line(in_file):
        _content = filter_token_dict(_line)
        yield index, _content


def get_items(in_file):

    for index, content in get_content(in_file):
        for level, items in content.items():
            for item in items:
                if item not in IDENTIFIERS and check_item(item) is False and is_integer(item) is False:
                    possible_correction = get_possible_correction(item)
                    yield index, item, possible_correction


def run(in_file):
    dir_name = os.path.dirname(in_file)
    raw_filename = os.path.splitext(os.path.basename(in_file))[0]
    out_file = pathmaker(dir_name, f"{raw_filename}_errors.txt")
    with open(out_file, 'w') as out_f:
        heading = f"Errors for {os.path.basename(in_file)}:"
        out_f.write(heading + '\n\n')
        print('\n' + heading + '\n\n')
        found_errors = 0
        for _index, x_item, pos_correct in get_items(in_file):
            if '\\' in x_item:
                text = f'line: {str(_index)}{" "*(REPORT_SPACING_1-len(str(_index)))} -> "{x_item}"{" "*(REPORT_SPACING_2-len(str(x_item)))} | is this maybe an file path?'
            else:
                if pos_correct is None:
                    pos_correct = "NO POSSIBLE CORRECTION FOUND"

                text = f'line: {str(_index)}{" "*(REPORT_SPACING_1-len(str(_index)))} -> "{x_item}"{" "*(REPORT_SPACING_2-len(str(x_item)))} | did you maybe mean  --> {" "*REPORT_SPACING_1} "{pos_correct}"'

            print(text)
            found_errors += 1
            out_f.write(text + '\n')
        footer = '\n\n\n' + '#' * 25 + '\n\nFound Errors: ' + str(found_errors) + '\n\n\n'
        print(footer)
        out_f.write(footer)
# region[Main_Exec]


if __name__ == '__main__':
    pass
# endregion[Main_Exec]
