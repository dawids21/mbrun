#!/bin/env python3

from sys import argv, exit
from subprocess import Popen, PIPE
from helpers import mbrofi

# user variables

# application variables
mbconfig = mbrofi.parse_config()
dictionary_file = 'slovnyk_pl-en'
dictionary_inverse_file = 'slovnyk_en-pl'
BIND_TOGGLE = 'alt-t'
rofi_lines = None
script_ident = 'translate'
if script_ident in mbconfig:
    dictionary_file = mbconfig[script_ident].get("dictionary_file",
                                                 fallback='dictd_www.dict.org_gcide')
    dictionary_inverse_file = mbconfig[script_ident].get("thesaurus_file",
                                                         fallback='Moby Thesaurus II')
    BIND_TOGGLE = mbconfig[script_ident].get("bind_toggle", fallback="alt-t")
    rofi_lines = mbconfig[script_ident].get("rofi_lines", fallback=None)

if rofi_lines == "None":
    rofi_lines = None

# launcher variables
prompt = "translate: "
filt = ""

# run correct launcher with prompt and help message
launcher_args = {}
launcher_args['prompt'] = prompt
launcher_args['filter'] = filt
launcher_args['format'] = 'f'
launcher_args['bindings'] = [BIND_TOGGLE]


def translate(word, inverse=False):
    """Send word to sdcv dictionary and return results"""
    if inverse:
        proc = Popen(
            ['sdcv', '-n', '-u', dictionary_inverse_file, word], stdout=PIPE)
    else:
        proc = Popen(['sdcv', '-n', '-u', dictionary_file, word], stdout=PIPE)
    ans = proc.stdout.read().decode('utf-8')
    exit_code = proc.wait()
    if exit_code == 1:
        print("sdcv failed...exiting")
        exit(1)
    else:
        entries = []
        templist = ans.strip().split('\n')
        for entry in templist:
            if entry.startswith('-'):
                continue
            entries.append(entry)
        return(entries)


def main(launcher_args, query=None, inverse=False, rofi_lines=None):
    """Main function."""
    while True:
        if inverse:
            launcher_args['prompt'] = "english: "
        else:
            launcher_args['prompt'] = "polish: "
        launcher_args['mesg'] = "Press '" + BIND_TOGGLE
        launcher_args['mesg'] += "' to show switch languages."
        if query is None:
            answer, exit_code = mbrofi.rofi([], launcher_args)
        else:
            if rofi_lines is None:
                theme_args = ["-theme-str", "#window {width: 38em;}"]
                theme_args.append("-i")
                theme_args.append("-markup-rows")
                answer, exit_code = mbrofi.rofi(translate(query, inverse),
                                                launcher_args, theme_args)
            else:
                theme_args = ["-theme-str",
                              "#window {width: 38em;}" +
                              " #window.mainbox.listview { lines: " +
                              rofi_lines + ";}"]
                theme_args.append("-i")
                theme_args.append("-markup-rows")
                answer, exit_code = mbrofi.rofi(translate(query, inverse),
                                                launcher_args, theme_args)
        if (exit_code == 1):
            break
        if not answer:
            if exit_code == 10:
                inverse = not(inverse)
                continue
            else:
                break
        elif (exit_code == 0):
            filt = answer.strip()
            query = filt
        elif (exit_code == 10):
            inverse = not(inverse)
            filt = answer.strip()
            query = filt
        elif (exit_code == 11):
            filt = answer.strip()
            if not filt:
                continue
            break
        else:
            break


if __name__ == '__main__':
    if (len(argv) > 1):
        if argv[1] == '-i':
            inverse = True
            query = ''.join(str(e) + ' ' for e in argv[2:]).strip()
        else:
            inverse = False
            query = ''.join(str(e) + ' ' for e in argv[1:]).strip()
        main(launcher_args, query, inverse, rofi_lines=rofi_lines)
    else:
        query = None
        main(launcher_args, query, rofi_lines=rofi_lines)
