# Python Script used to 'manage' downloaded archives from Nexus Mods

import os, re, code, json, shutil, subprocess, webbrowser
from patoolib import (check_archive_format,
                      check_program_compression,
                      find_archive_program,
                      get_archive_cmdlist_func,
                      get_archive_format,
                      )
from patoolib.util import run_under_pythonw
from random import randint
from blessed import Terminal
from blessed.sequences import Sequence

RE_STDOUT = re.compile(r"(?:(?:\.{4}A)|(?:\.{5}))(?:\s*\d+){2}\s+([-+`~!@#$%^&_+/,.;'\w\\ \(\)\[\]\{\}]+)", re.I)
RE_STDLN = re.compile(r'[\r\n]+', re.I)
RE_STDPTH = re.compile(r'\\', re.I)

RE_SEARCH = lambda string: re.compile(re.sub(r"\s+", '.*?', string, re.I), re.I)

ACPROG = {}
ACMDLS = {}
Archive_Content = {}

if os.path.exists('_Archive_Content.json'):
    with open('_Archive_Content.json', 'r') as fp:
        Archive_Content = json.load(fp)
        fp.close()

def build_content():
    global Archive_Content
    for mid, content in MODS.items():
        for name, package in content.items():
            for ver, path in package.items():
                Archive_Content[path] = lsarc(path)
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

def link(n):
    webbrowser.open(f"https://www.nexusmods.com/cyberpunk2077/mods/{n}")

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

UNSORT = '__unsorted'

REGP = lambda string: rf"(?:{string})"
REOR = lambda *terms: f"{'|'.join([REGP(e) for e in terms])}"

RE_DIR = re.compile(r'^__[a-zA-Z]+.*', re.I)
RE_MID = re.compile(r'(?<=\n)(?P<PTH>(?P<DIR>\w+)/(?P<NAM>.*?)-(?P<MID>\d\d\d+)-(?P<VER>\w+(?:-\w+)*)-(?P<HSH>\d+)\.(?P<EXT>\w+))', re.I)
RE_NAM = re.compile(r'[-_ ]+', re.I)
RE_VER = re.compile(r'(?:(?:\sv?\d+)(?:[\._-abc]\d+)+x?(?:zip|rar)?|(?:\sv\d+)|(?:(?:re)?v\d+(?=[ :$])))(?:[\._-abc])?\d*(?:zip|rar)?', re.I)
namfy = lambda name: RE_VER.sub(' VER', RE_NAM.sub(' ', name.lower()))

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
versort = lambda package: sorted(package.items(), key=lambda e: e[0], reverse=True)

lnam = lambda string: string if len(string) < _NAMLEN-1 else f"{string[:_NAMLEN-5]}..."
lver = lambda string: string if len(string) < _VERLEN-1 else f"{string[:_VERLEN-5]}..."
ckey = lambda string: TERM.green_on_black(lnam(string) + ':')
cver = lambda string, i: TERM.green_on_black(f"{lver(string.lstrip())+': ':{_VERLEN}}") if i==0 else TERM.yellow_on_black(f"{' '*(_NAMLEN+8)}{lver(string)+': ':{_VERLEN}}")

def scan(debug=False):
    global DB, DIRS, MODS, PATHS
    clear()
    DB = []
    DIRS = []
    PATHS = []
    MODS = {}
    DIRS = [e for e in os.listdir() if RE_DIR.match(e.lower()) and not '.' in e]
    if debug: print('\n'.join([e for e in DIRS]))
    PATHS = [f"{f}/{e}" for f in DIRS for e in os.listdir(f)]
    DB = [e.groupdict() for e in RE_MID.finditer('\n'+'\n'.join(PATHS))]
    MODS = {int(e[MID]):{HSH:{}} for e in DB}
    for e in DB:
        name, mid, ver, hsh, pth = namfy(e[NAM]), int(e[MID]), e[VER], int(e[HSH]), e[PTH]
        if hsh not in MODS[mid][HSH].keys():
            MODS[mid][HSH].update({hsh:{NAM:name, VER:ver}})
        else:
            if name != MODS[mid][HSH][hsh][NAM] or ver != MODS[mid][HSH][hsh][VER]:
                print(f"Inconsistent name/ver/hash - {e[MID]}:{hsh}: {'-'.join(MODS[MID][HSH][hsh].values())} and {name}-{ver}")
                if debug: code.interact(local=locals())
        if name not in MODS[mid].keys():
            MODS[mid][name] = {}
            MODS[mid][name][ver] = pth
        elif ver in MODS[mid][name].keys():
            hshs = [k for k, v in MODS[mid][HSH].items() if name==v[NAM] and k != hsh]
            last = max(hshs + [0,])
            if hsh > last:
                MODS[mid][name][f".{len(hshs)+1}"] = MODS[mid][name][ver]
                MODS[mid][name][ver] = pth
            elif hsh == last:
                if UNSORT in MODS[mid][name][ver]:
                    MODS[mid][name][f".{len(hshs)+1}"] = MODS[mid][name][ver]
                    MODS[mid][name][ver] = pth
                else:
                    MODS[mid][name][f".{len(hshs)+1}"] = pth
            elif last != 0:
                MODS[mid][name][f".{len(hshs)+1}"] = pth
        else:
            MODS[mid][name].update({ver:pth})

        #     print(f"Inconsistent Mod ID - {e[NAM]}: {MODS[e[NAM]][MID]} / {e[MID]}")
        # if VER not in MODS[e[NAM]].keys():
        #     MODS[e[NAM]][VER] = {e[VER]: e[PTH]}
        # else:
        #     MODS[e[NAM]][VER].update({e[VER]: e[PTH]})

TABS = lambda n: '\n' + '\t'*n

def dict_concat(d, mode=1, depth=0):
    match d:
        case list()|tuple()|set():
            return TABS(depth).join((dict_concat(e, mode, depth) for e in d))
        case dict():
            if any(isinstance(e, dict) for e in d.values()):
                if not depth:
                    return TABS(depth).join(f"{k}\t{dict_concat(v, mode, depth+1)}" for k, v in d.items())
                else:
                    return TABS(depth).join(f"{dict_concat(v, mode, depth+1)}" for v in d.values())
            else:
                match mode:
                    case 0: return TABS(depth).join(f"{e}" for e in d.keys())
                    case 1: return TABS(depth).join(f"{e}" for e in d.values())
                    case _: return TABS(depth).join(f"{k}:{v}" for k, v in d.items())
        case _: print(f"{d=:<80}, {mode=}")

LFS = []
LFT = ''
LML = []

def lml(n=0):
    listed = list(LML.keys())
    if n > 0:
        return listed[:n]
    elif n < 0:
        return listed[n:]
    else:
        return listed

def setlast(filt, mods):
    global LFS, LFT, LML
    if filt:
        LFT = filt
        if filt in LFS: LFS.remove(LFT)
        LFS.append(LFT)
        LML = mods

def paths(filt='', sortbyname=False):
    scan()
    global MODS
    mods = {}
    for mid, content in sorted(MODS.items(), key=lambda e: e[0] if not sortbyname else list(e[1].keys())[0]):
        if (not filt and len(content.keys())>0) or (filt and RE_SEARCH(filt).search(dict_concat(content), re.I)):
            mods[mid] = MODS[mid]
    setlast(filt, mods)
    return mods

def ppaths(filt='', sortbyname=False):
    clear()
    global MODS
    mods = paths(filt, sortbyname)
    setlast(filt, mods)
    for mid, content in mods.items():
        for key in [e for e in content.keys() if e != HSH]:
            print(f"{mid:>{_MIDLEN-1}}:{ckey(key):{_NAMLEN+16}}{newline_join([f"{cver(f"{k}", i)}{v}" for i, (k, v) in enumerate(versort(content[key]))])}")
    print(f"{len(MODS)} mods found")

upaths = lambda filt='', sortbyname=False: ppaths(UNSORT+' '+filt, sortbyname)

def getmods(input_value):
    global MODS
    match input_value:
        case int():
            return [MODS[input_value]]
        case str():
            return [MODS[mid] for mid, content in MODS.items() if RE_SEARCH(input_value).search('\n'.join(content.keys()))]
        case dict():
            if all([isinstance(e, int) for e in input_value.keys()]):
                return list(input_value.values())
        case list():
            if all([isinstance(e, dict) for e in input_value]) and all([isinstance(e, int) for e in input_value.keys()]):
                return input_value
            elif all([isinstance(e, int) for e in input_value]):
                return [MODS[e] for e in input_value if e in MODS.keys()]
            else:
                print(f"Unhandled Input Value: {input_value}"); return []
        case _:
            print(f"Unhandled Input Value: {input_value}"); return []

def resolve_fuzzypath(fuzzypath):
    if len(result:=[e for e in os.listdir() if RE_SEARCH(fuzzypath).search(e) and os.path.isdir(e)])==1:
        return result[0]
    else:
        print("Ambiguous path resolution or path does not exist.")
        return None

def fcheck(fuzzypath):
    path = resolve_fuzzypath(fuzzypath)
    if path:
        with open(f"{path}.txt", 'r') as fp:
            modlist = [int(e) for e in fp.read().split('\n')]
            mods = getmods(modlist)
        fp.close()
        modlist = [e for e in modlist if e not in MODS.keys()]
        return modlist
    else:
        print(f"Move instruction cancelled")

def fsort(fuzzypath):
    path = resolve_fuzzypath(fuzzypath)
    if path:
        with open(f"{path}.txt", 'r') as fp:
            modlist = [int(e) for e in fp.read().split('\n')]
            mods = getmods(modlist)
            if not mods: print(f"Input mods not found."); return
            for m in mods:
                for name, package in m.items():
                    for i, verpath in enumerate(versort(package)):
                        shutil.move(verpath[1], f"{path}/{os.path.basename(verpath[1])}")
        fp.close()
        print(f"These mods are currently not found in local repository{fcheck(fuzzypath)}")
    else:
        print(f"Move instruction cancelled")

def clean(input_value, force=False):
    mods = getmods(input_value)
    if not mods: print(f"Input mods not found."); return
    if not os.path.exists('___CLEAN/'): os.mkdir('___CLEAN/')
    for m in mods:
        for name, package in m.items():
            if name == HSH: continue
            for i, verpath in enumerate(versort(package)):
                if i>0 or force: shutil.move(verpath[1], f"___CLEAN/{os.path.basename(verpath[1])}")

def move(input_value, fuzzypath):
    mods = getmods(input_value)
    if not mods: print(f"Input mods not found."); return
    path = resolve_fuzzypath(fuzzypath)
    if path:
        for m in mods:
            for name, package in m.items():
                if name == HSH: continue
                for i, verpath in enumerate(versort(package)):
                    shutil.move(verpath[1], f"{path}/{os.path.basename(verpath[1])}")
    else:
        print(f"Move instruction cancelled")

mvvh = lambda input_value: move(input_value, "__Vehicles")

while True:
    upaths()
    code.interact(local=locals())

