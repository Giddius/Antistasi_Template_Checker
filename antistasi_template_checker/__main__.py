

# region [Imports]

# * Standard Library Imports ------------------------------------------------------------------------------------------------------------------------------------>

import os
import sys
import time
# * Local Imports ----------------------------------------------------------------------------------------------------------------------------------------------->

from antistasi_template_checker.antistasi_template_parser import run

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [AppUserData]


# endregion [AppUserData]

# region [Logging]


# endregion[Logging]

# region [Constants]


# endregion[Constants]


def main(in_file):

    if os.path.exists(in_file) is False:
        raise FileNotFoundError(in_file)
    if os.path.isfile(in_file) is False:
        raise FileNotFoundError(in_file)
    run(in_file)


# region[Main_Exec]


if __name__ == '__main__':
    for index, input_file in enumerate(sys.argv):
        if index != 0:
            main(input_file)
            print('#' * 10 + f' finished file "{input_file}"')

    os.system("pause")

# endregion[Main_Exec]
