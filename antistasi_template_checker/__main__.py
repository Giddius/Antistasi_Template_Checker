
"""

[summary]

"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import sys

# * Third Party Imports --------------------------------------------------------------------------------->
import click

# * Local Imports --------------------------------------------------------------------------------------->
from antistasi_template_checker.engine.antistasi_template_parser import run, readit, pathmaker

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [AppUserData]


# endregion [AppUserData]

# region [Logging]


# endregion[Logging]

# region [Constants]


# endregion[Constants]


def get_outfile_name(in_file):
    name = os.path.basename(in_file)
    path = os.path.dirname(in_file)
    mod_name = os.path.splitext(in_file)[0]
    return pathmaker(path, f"{mod_name}_ERRORS.txt")


@click.group()
def cli():
    pass


@cli.command(name="get_source")
def get_source_string():
    print('currently not possible with pyinstaller to inspect source data in an single file executable')


@cli.command(name="from_file")
@click.option('--case-insensitive/--case-sensitive', '-ci/-cs', default=False)
@click.option('--write-to-file/--dont-write-to-file', '-wf/-dwf', default=False)
@click.option('--pause-at-end/--no-pause-at-end', '-p/-np', default=False)
@click.option('--make-replacement/--dont-make-replacement', '-mr/-dmr', default=True)
@click.argument('in_files', nargs=-1)
def from_file(case_insensitive, write_to_file, pause_at_end, in_files, make_replacement):
    for file in in_files:
        if os.path.isfile(file) is False:
            raise FileNotFoundError(file)
        content = readit(file)
        result = run(content, case_insensitive=case_insensitive)
        if write_to_file is True:
            with open(get_outfile_name(file), 'w') as out_f:
                out_f.write(f"Errors in '{os.path.basename(file)}':\n\n\n")
                out_f.write(result[0])
        if make_replacement is True and len(result[1]) != 0:
            _new_file_name = os.path.splitext(os.path.basename(file))[0] + '_CORRECTED' + os.path.splitext(file)[-1]
            _new_file_path = pathmaker(os.path.dirname(file), _new_file_name)
            _new_content = content
            for old_item, new_item in result[1]:
                _new_content = _new_content.replace(old_item, new_item)
            with open(_new_file_path, 'w') as cor_f:
                cor_f.write(_new_content)
            if len(result[2]) != 0:
                print('\n\n')
                print(f'not corrected in "{_new_file_name}":\n')
                for _line, _not_corrected_item in result[2]:
                    print(f'line: {str(_line)} <> "{_not_corrected_item}"\n')
                print('\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n')

    if pause_at_end is True:
        os.system('pause')


def main():
    if sys.argv[1] not in ['from_file', 'get_source', '--help']:
        first = sys.argv.pop(0)
        sys.argv = [first, 'from_file'] + sys.argv

    cli(sys.argv[1:])

# region[Main_Exec]


if __name__ == '__main__':
    main()

# endregion[Main_Exec]
