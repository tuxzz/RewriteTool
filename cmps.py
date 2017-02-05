import os
import pickle, shutil
from ssmanager import SSManager
from gameexe import Gameexe

oPath = r"E:\hackbase\ss_rwn\scene_orig"
cPath = r"E:\hackbase\ss_rwn\scene_chs"
nPath = r"E:\hackbase\ss\scene"
poPath = r"D:\Desktop\scene_call"
outPath = r"D:\Desktop\scene_out"
gexePath = r"E:\hackbase\ss\Gameexe.ini"

gexe = Gameexe()
gexe.load(open(gexePath, "rb").read().decode("utf-16").split("\n"))

sceneDict = {}
outputContextRadius = 6
matchContextRadius = 4

try:
    shutil.rmtree(poPath)
    shutil.rmtree(outPath)
except:
    pass
os.makedirs(poPath)
os.makedirs(outPath)

def matchContext(l, i, dummyIndex, processor, radius):
    above, below = processor[:2]
    nAb, nBl = getContext(l, i, dummyIndex, radius)
    return nAb == above and nBl == below

def getContext(l, i, dummyIndex, radius):
    return l[max(0, i - matchContextRadius):i], l[i + 1:min(i + matchContextRadius + 1, dummyIndex)]

def allAscii(s):
    return all(ord(c) < 128 for c in s)

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
        if(ext != ".ss"):
            continue
        if(not basename in sceneDict):
            entry = {}
            sceneDict[basename] = entry
        else:
            entry = sceneDict[basename]
        entry["o"] = {"path": path, "size": fSize}

for p, d, f in os.walk(cPath):
    for fn in f:
        path = os.path.join(p, fn)
        fInfo = {}
        fSize = os.stat(path).st_size
        basename, ext = os.path.splitext(fn)
        if(ext != ".ss"):
            continue
        if(not basename in sceneDict):
            entry = {}
            sceneDict[basename] = entry
        else:
            entry = sceneDict[basename]
        entry["c"] = {"path": path, "size": fSize}

for p, d, f in os.walk(nPath):
    for fn in f:
        path = os.path.join(p, fn)
        fInfo = {}
        fSize = os.stat(path).st_size
        basename, ext = os.path.splitext(fn)
        if(ext != ".ss"):
            continue
        if(not basename in sceneDict):
            entry = {}
            sceneDict[basename] = entry
        else:
            entry = sceneDict[basename]
        entry["n"] = {"path": path, "size": fSize}

diff = {}
same = {}
rm = {}
new = {}

for i, (basename, entry) in enumerate(sceneDict.items()):
    oHas = "o" in entry
    cHas = "c" in entry
    nHas = "n" in entry
    if(oHas and not nHas):
        remove[basename] = entry
        continue
    if(nHas and not oHas):
        new[basename] = entry
        continue
    isDiff = entry["o"]["size"] != entry["n"]["size"]
    if(not isDiff):
        isDiff = bytecmp(entry["o"]["path"], entry["n"]["path"])
    if(isDiff):
        diff[basename] = entry
        continue
    same[basename] = entry

# string match
untranslatedDict = {}
for iEntry, (basename, entry) in enumerate(diff.items()):
    print(iEntry ,"/", len(diff))

    # load and check datas
    orig = SSManager()
    chs = SSManager()
    plus = SSManager()
    orig.load(open(entry["o"]["path"], "rb").read())
    chs.load(open(entry["c"]["path"], "rb").read())
    plus.load(open(entry["n"]["path"], "rb").read())
    origDummyIndex = orig.stringList.index("dummy")
    chsDummyIndex = chs.stringList.index("dummy")
    plusDummyIndex = plus.stringList.index("dummy")
    assert(origDummyIndex == chsDummyIndex)
    assert(origDummyIndex != -1)
    assert(plusDummyIndex != -1)
    if(origDummyIndex < len(orig.stringList) - 1):
        assert(all(allAscii(x) for x in orig.stringList[origDummyIndex:]))
        assert(all(allAscii(x) for x in chs.stringList[chsDummyIndex:]))
        assert(all(allAscii(x) for x in plus.stringList[plusDummyIndex:]))

    # collect confliction
    sentenceDict = {}
    conflictDict = {}
    tempDict = {}
    for i, origSentence in enumerate(orig.stringList[:origDummyIndex]):
        if(not origSentence or origSentence in gexe.namae):
            continue
        translatedStr = chs.stringList[i]
        inDict = tempDict.get(origSentence, None)
        if(inDict is None):
            inDict = []
            tempDict[origSentence] = inDict
        inDict.append(translatedStr)

    tempDict = {k: len(set(v)) for k, v in tempDict.items()}

    for i, origSentence in enumerate(orig.stringList[:origDummyIndex]):
        if(not origSentence or origSentence in gexe.namae):
            continue
        translatedStr = chs.stringList[i]
        if(tempDict[origSentence] > 1):
            ctx = (*getContext(orig.stringList, i, origDummyIndex, matchContextRadius), translatedStr)

            processList = conflictDict.get(origSentence, None)
            if(processList is None):
                processList = []
                conflictDict[origSentence] = processList
            processList.append(ctx)
    del tempDict

    # build sentenceDict
    for i, origSentence in enumerate(orig.stringList[:origDummyIndex]):
        if(not origSentence or origSentence in gexe.namae):
            continue
        if(not origSentence in conflictDict):
            sentenceDict[origSentence] = chs.stringList[i]

    # translate plus
    nMiss = 0
    nHit = 0
    untranslatedPlusStringList = list(plus.stringList)
    for i, plusSentence in enumerate(plus.stringList[:plusDummyIndex]):
        if(not plusSentence or plusSentence in gexe.namae):
            continue
        conflictProcessorList = conflictDict.get(plusSentence, None)
        hit = False
        if(conflictProcessorList is not None):
            for processor in conflictProcessorList:
                if(matchContext(untranslatedPlusStringList, i, plusDummyIndex, processor, matchContextRadius)):
                    plus.stringList[i] = processor[2]
                    hit = True
        else:
            translatedStr = sentenceDict.get(plusSentence, None)
            if(translatedStr is not None):
                plus.stringList[i] = translatedStr
                hit = True
        if(not hit):
            nMiss += 1
            ctxUntranslated = getContext(untranslatedPlusStringList, i, plusDummyIndex, outputContextRadius)
            ctxTranslated = getContext(plus.stringList, i, plusDummyIndex, outputContextRadius)
            l = untranslatedDict.get(plusSentence, None)
            if(l is None):
                l = []
                untranslatedDict[plusSentence] = l
            l.append((ctxUntranslated, ctxTranslated))
        else:
            nHit += 1
    if(nMiss):
        pickle.dump(untranslatedDict, open(os.path.join(poPath, "%s.pickle" % (basename,)), "wb"))
        print("Missed %d / %d" % (nMiss, nMiss + nHit))

    open(os.path.join(outPath, "%s.ss" % (basename,)), "wb").write(plus.dump())

print("Total:", len(sceneDict))
print("Same:", len(same))
print("Removed:", len(rm))
print("New:", len(new))
print("    %s" % (str(list(new.keys()))))
