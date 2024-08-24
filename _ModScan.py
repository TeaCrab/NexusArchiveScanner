import os, re, code, shutil, subprocess, webbrowser
from patoolib import (check_archive_format,
                      check_program_compression,
                    #   extract_archive,
                      find_archive_program,
                      get_archive_cmdlist_func,
                      get_archive_format,
                      )
from patoolib.util import run_under_pythonw
import json
from random import randint
# from io import StringIO
from blessed import Terminal
from blessed.sequences import Sequence
# Python Script used to 'manage' downloaded archives from Nexus Mods

RE_STDOUT = re.compile(r"(?:(?:\.{4}A)|(?:\.{5}))(?:\s*\d+){2}\s+([-+`~!@#$%^&_+/,.;'\w\\ \(\)\[\]\{\}]+)", re.I)
RE_STDLN = re.compile(r'[\r\n]+', re.I)
RE_STDPTH = re.compile(r'\\', re.I)

ACPROG = {}
ACMDLS = {}
Archive_Content = {}

if os.path.exists('_Archive_Content.json'):
    with open('_Archive_Content.json', 'r') as fp:
        Archive_Content = json.load(fp)
        fp.close()

def build_content():
    global Archive_Content
    Archive_Content = {get_path(mod):lsarc(get_path(mod)) for mod in MODS.values()}
    json.dump(Archive_Content, open('Archive_Content.json', 'w'))

def capcmd(apath):
    if os.path.exists(apath) and os.access(apath, os.R_OK):
        aform, acomp = get_archive_format(apath)
        if aform in ACPROG.keys() and acomp in ACPROG[aform].keys():
            aprog = ACPROG[aform][acomp]
        else:
            check_archive_format(aform, acomp)
            aprog = find_archive_program(aform, 'list', None, None)
            check_program_compression(apath, 'list', aprog, acomp)
            if aform not in ACPROG.keys(): ACPROG[aform] = {}
            if acomp not in ACPROG[aform].keys(): ACPROG[aform][acomp] = aprog
        if aprog in ACMDLS.keys() and aform in ACMDLS[aprog].keys():
            acmdlist = ACMDLS[aprog][aprog] + [apath]
        else:
            get_archive_cmdlist = get_archive_cmdlist_func(aprog, 'list', aform)
            acmdlist = get_archive_cmdlist(apath, acomp, aprog, 1, False, None)
            if aform not in ACMDLS.keys(): ACMDLS[aform] = {}
            if aprog not in ACMDLS[aform].keys(): ACMDLS[aform][aprog] = acmdlist[:-1]
        cmd, runargs = acmdlist if isinstance(acmdlist, tuple) else acmdlist, {}
        if run_under_pythonw():
            runargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        runargs['input']=""
        if runargs.get("shell"):
            cmd = " ".join(cmd)
        return subprocess.run(cmd, **runargs, capture_output=True)
    else:
        print("Archive File Not Found")

def lsarc(apath):
    # string = capcmd(apath).stdout
    # string = RE_STDLN.sub(r'\n', capcmd(apath).stdout.decode())
    # code.interact(local=locals())
    try: return RE_STDOUT.findall(RE_STDPTH.sub('/', RE_STDLN.sub(r'\n', capcmd(apath).stdout.decode())))
    except UnicodeDecodeError: return RE_STDOUT.findall(RE_STDPTH.sub('/', RE_STDLN.sub(r'\n', capcmd(apath).stdout.decode(encoding='latin-1'))))
    else: print(apath); input("Press any key to continue...")

_DIRLEN = 36
_MIDLEN = 8
_VERLEN = 16
_NAMLEN = 72

TERM = Terminal()
SEQU = lambda string: Sequence(string, TERM)

DB = []
DIRS = []
PATHS = []
MODS = {}

PTH = 'PTH'
DIR = 'DIR'
NAM = 'NAM'
MID = 'MID'
VER = 'VER'
HSH = 'HSH'
EXT = 'EXT'

random_mod = lambda: list(list(MODS.values())[randint(0, len(MODS)-1)][VER].values())[0]
get_path = lambda mod: list(mod[VER].values())[0]

REGP = lambda string: rf"(?:{string})"
REOR = lambda *terms: f"{'|'.join([REGP(e) for e in terms])}"

RE_DIR = re.compile(r'^__[a-z].*', re.I)
RE_MID = re.compile(r'(?<=\n)(?P<PTH>(?P<DIR>\w+)/(?P<NAM>.*?)-(?P<MID>\d\d\d+)-(?P<VER>\w+(?:-\w+)*)-(?P<HSH>\d+)\.(?P<EXT>\w+))', re.I)

RES = {
    re.compile(r".*/(archive/pc/mod/.*)", re.I),
    re.compile(r".*/(bin/x64/plugins/cyber engine tweaks/mods/.*)", re.I),
    re.compile(r".*/(r6/tweaks/.*)", re.I),
    re.compile(r".*/(r6/scripts/.*)", re.I),
    re.compile(r".*/(red4ext/plugins/.*)", re.I),
}

clear = lambda: os.system('cls')
print_mod = lambda e: print(f"{e[DIR]:<{_DIRLEN}}: {e[MID]:<{_MIDLEN}}{e[VER]:<{_VERLEN}}: {e[NAM]:{_NAMLEN}} {e[HSH]}")

newline_join = lambda array: '\n'.join([f"{e}" for e in array])
versort = lambda mod: sorted(mod[VER].items(), key=lambda e: e[0], reverse=True)

lnam = lambda string: string if len(string) < _NAMLEN-1 else f"{string[:_NAMLEN-5]}..."
lver = lambda string: string if len(string) < _VERLEN-1 else f"{string[:_VERLEN-5]}..."
ckey = lambda string: TERM.green_on_black(lnam(string) + ':')
cver = lambda string, i: TERM.green_on_black(f"{lver(string.lstrip())+': ':{_VERLEN}}") if i==0 else TERM.yellow_on_black(f"{' '*(_NAMLEN+8)}{lver(string)+': ':{_VERLEN}}")

def scan():
    global DB, DIRS, MODS, PATHS
    clear()
    DB = []
    DIRS = []
    PATHS = []
    MODS = {}
    DIRS = [e for e in os.listdir() if RE_DIR.match(e.lower()) and not '.' in e]
    PATHS = [f"{f}/{e}" for f in DIRS for e in os.listdir(f)]
    DB = [e.groupdict() for e in RE_MID.finditer('\n'+'\n'.join(PATHS))]
    MODS = {e[NAM]:{} for e in DB}
    for e in DB:
        if MID not in MODS[e[NAM]].keys():
            MODS[e[NAM]][MID] = e[MID]
        elif e[MID] != MODS[e[NAM]][MID]:
            print(f"Inconsistent Mod ID - {e[NAM]}: {MODS[e[NAM]][MID]} / {e[MID]}")
        if VER not in MODS[e[NAM]].keys():
            MODS[e[NAM]][VER] = {e[VER]: e[PTH]}
        else:
            MODS[e[NAM]][VER].update({e[VER]: e[PTH]})

def ppaths(show_all=False, sortkey=None):
    clear()
    global MODS
    mids = {}
    mods = []
    for key, value in MODS.items():
        if value[MID] in mids.keys(): mids[value[MID]] += [key]
        else: mids[value[MID]] = [key]
    for key, value in sorted(MODS.items(), key=lambda e: e[0] if not sortkey else e[1][sortkey]):
        if len(value[VER])>1 or (value[MID] in mids.keys() and (len(mids[value[MID]])>1 or key not in mids[value[MID]])) or show_all:
            mods += [MODS[key]]
            print(f"{value[MID]:>{_MIDLEN-1}}:{ckey(key):{_NAMLEN+16}}{newline_join([f"{cver(k, i)}{v}" for i, (k, v) in enumerate(versort(value))])}")
    print(f"{len(MODS)} mods found")

def paths(get_all=False):
    global MODS
    mods = []
    for key, value in MODS.items() or get_all:
        if len(value[VER])>1: mods += [MODS[key]]
    return mods

def modds(db):
    clear()
    for e in sorted(db, key=lambda e: [e[NAM], e[VER]]):
        print_mod(e)
    print(f"{len(db)} mods found")

def filter(key, term):
    global DB
    RE = re.compile(term, re.I)
    return sorted([e for e in DB if RE.search(e[key])], key=lambda e: [e[NAM], e[VER]])

def getmods(input_value):
    global MODS
    match input_value:
        case int():
            return [MODS[key] for key in MODS.keys() if int(MODS[key][MID])==input_value]
        case str():
            RE = re.compile(input_value, re.I)
            return [MODS[key] for key in MODS.keys() if RE.search(key)]
        case list():
            if all([isinstance(e, dict) for e in input_value]):
                return [e for e in input_value if MID in e.keys()]
            else:
                print(f"Unhandled Input Value: {input_value}"); return []
        case _:
            print(f"Unhandled Input Value: {input_value}"); return []

def clean(input_value):
    mods = getmods(input_value)
    if not mods: print(f"Input mods not found."); return
    if not os.path.exists('___CLEAN/'): os.mkdir('___CLEAN/')
    for m in mods:
        for i, kv in enumerate(versort(m)):
            if i>0: shutil.move(kv[1], f"___CLEAN/{os.path.basename(kv[1])}")

# def move(mod, name):
#     shutil.move()

# def delete(input_value):
#     mods = getmods(input_value)
#     if not mods: print(f"Input mods not found."); return
#     confirmation = input("Enter 'DELETE' to proceed with deleting specified mods:")
#     if confirmation!='DELETE': print("Deletion Cancelled"); return
#     if not os.path.exists('___DELETE/'): os.mkdir('___DELETE/')
#     for m in mods:
#         for fpth in m[VER].values():
#             shutil.move(fpth, f"___DELETE/{os.path.basename(fpth)}")

# def check_struc(path=None):
#     path = path if path else '.temp/'
#     file_list = []
#     for root, _, files in os.walk(path):
#         file_list += {f"{root}/{f}" for f in files}
#     return file_list

# def apply_struc(path=None):
#     file_list = check_struc(path)
#     for fpth in file_list:
#         shutil.move(fpth, )

# def extract(input_value):
#     mods = getmods(input_value)
#     if not mods: print(f"Input mods not found."); return
#     if not os.path.exists('_STAGING/'): os.mkdir('_STAGING/')
#     if not os.path.exists('.temp/'): os.mkdir('.temp/')
#     # shutil.rmtree('.temp/*')
#     for m in mods:
#         for _, fpth in versort(m)[0]:
#             extract_archive(fpth, outdir=f".temp/")

def link(n):
    webbrowser.open(f"https://www.nexusmods.com/cyberpunk2077/mods/{n}")

while True:
    scan()
    code.interact(local=locals())

