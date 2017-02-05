from ssmanager import SSManager

path = r"E:\hackbase\ss\scene\seen01001.ss"
out = r"D:\Desktop\s01001.ss"

data = open(path, "rb").read()

m = SSManager()
m.load(data)
open(out, "wb").write(m.dump())

print(m.stringList)
print("FirstPos:", m.firstPos)
print("HasSignature:", m.hasSignature())
print("Total:", len(m.stringList))
