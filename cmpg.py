import os
from shutil import copyfile

oPath = r"E:\Games\Rewrite\g00"
nPath = r"E:\Games\RewritePLUS\g00"

translatedOPath = r"D:\Desktop\tr_o"
translatedCPath = r"D:\Desktop\tr_c"
translatedNPath = r"D:\Desktop\tr_n"

dntOPath = r"D:\Desktop\dnt_o"
dntCPath = r"D:\Desktop\dnt_c"
dntNPath = r"D:\Desktop\dnt_n"

diffOPath = r"D:\Desktop\diff_o"
diffNPath = r"D:\Desktop\diff_n"

newNPath = r"D:\Desktop\new_n"

gDict = {}

def bytecmp(a, b):
    f1 = open(a, "rb").read()
    f2 = open(b, "rb").read()
    return f1 != f2

for p, d, f in os.walk(oPath):
    for fn in f:
        path = os.path.join(p, fn)
        fInfo = {}
        fSize = os.stat(path).st_size
        basename, ext = os.path.splitext(fn)
        if(not basename in gDict):
            entry = {}
            gDict[basename] = entry
        else:
            entry = gDict[basename]
        if(ext == ".g00"):
            entry["o"] = {"path": path, "size": fSize}
        elif(ext == ".g01"):
            entry["c"] = {"path": path, "size": fSize}
        else:
            assert(False)

for p, d, f in os.walk(nPath):
    for fn in f:
        path = os.path.join(p, fn)
        fInfo = {}
        fSize = os.stat(path).st_size
        basename, ext = os.path.splitext(fn)
        if(not basename in gDict):
            entry = {}
            gDict[basename] = entry
        else:
            entry = gDict[basename]
        if(ext == ".g00"):
            entry["n"] = {"path": path, "size": fSize}
        else:
            assert(False)

diff = {}
new = {}
rm = {}
translated = {}
dnt = {}

for iG00, (basename, entry) in enumerate(gDict.items()):
    if(iG00 % 100 == 0):
        print(iG00, "/", len(gDict))
    oHas = "o" in entry
    cHas = "c" in entry
    nHas = "n" in entry
    if(oHas and not nHas):
        rm[basename] = entry
        continue
    if(nHas and not oHas):
        new[basename] = entry
        continue
    isDiff = entry["o"]["size"] != entry["n"]["size"]
    if(not isDiff):
        isDiff = bytecmp(entry["o"]["path"], entry["n"]["path"])
    if(isDiff):
        if("c" in entry):
            dnt[basename] = entry
            continue
        diff[basename] = entry
        continue
    if("c" in entry):
        translated[basename] = entry

print("Translated g00:")
for basename, entry in translated.items():
    print("    %s" % (basename,))
print("")

print("Different and need-translate g00:")
for basename, entry in dnt.items():
    print("    %s" % (basename,))
print("")

print("Other Different g00:")
for basename, entry in diff.items():
    print("    %s" % (basename,))
print("")
print("New g00:")
for basename, entry in new.items():
    print("    %s" % (basename,))

os.makedirs(translatedOPath)
os.makedirs(translatedCPath)
os.makedirs(translatedNPath)
os.makedirs(dntOPath)
os.makedirs(dntCPath)
os.makedirs(dntNPath)
os.makedirs(diffOPath)
os.makedirs(diffNPath)
os.makedirs(newNPath)

print("total:", len(gDict))
print("translated:", len(translated))
print("dnt:", len(dnt))
print("diff:", len(diff))
print("removed:", len(rm))
print("new:", len(new))


print("Begin copy...")
for basename, entry in translated.items():
    copyfile(entry["o"]["path"], "%s.g00" % (os.path.join(translatedOPath, basename),))
    copyfile(entry["c"]["path"], "%s.g00" % (os.path.join(translatedCPath, basename),))
    copyfile(entry["n"]["path"], "%s.g00" % (os.path.join(translatedNPath, basename),))

for basename, entry in dnt.items():
    copyfile(entry["o"]["path"], "%s.g00" % (os.path.join(dntOPath, basename),))
    copyfile(entry["c"]["path"], "%s.g00" % (os.path.join(dntCPath, basename),))
    copyfile(entry["n"]["path"], "%s.g00" % (os.path.join(dntNPath, basename),))

for basename, entry in diff.items():
    copyfile(entry["o"]["path"], "%s.g00" % (os.path.join(diffOPath, basename),))
    copyfile(entry["n"]["path"], "%s.g00" % (os.path.join(diffNPath, basename),))

for basename, entry in new.items():
    copyfile(entry["n"]["path"], "%s.g00" % (os.path.join(newNPath, basename),))
print("copied")
