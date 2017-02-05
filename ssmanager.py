import struct
import io

def xorCrypt(x, key):
    key *= 0x7087
    key &= 0xFFFFFFFF
    o = bytearray(len(x))
    for i in range(0, len(x) - 1, 2):
        v2 = (key >> 8) & 0xFF
        v1 = key & 0xFF
        o[i] = x[i] ^ v1
        o[i + 1] = x[i + 1] ^ v2
    return bytes(o)

class Entry:
    def __init__(self, data):
        self.pos, self.length = struct.unpack("<II", data)

    @staticmethod
    def pack(pos, length):
        return struct.pack("<II", pos, length)

class SSManager:
    def __init__(self):
        self.signature = bytes((0x00, 0x53, 0x69, 0x67, 0x6C, 0x75, 0x73, 0x53, 0x63, 0x72, 0x69, 0x70, 0x74, 0x4D, 0x61, 0x6E, 0x61, 0x67, 0x65, 0x72))

    def load(self, data):
        assert(isinstance(data, bytes))
        self.data = data
        self.firstPos = len(data)

        offsetTable = Entry(data[0xC:0xC + 8])
        stringTable = Entry(data[0x14:0x14 + 8])

        content = []
        for i in range(stringTable.length):
            offset = offsetTable.pos + i * 8
            strEntry = Entry(data[offset:offset + 8])
            pos = (strEntry.pos * 2) + stringTable.pos # *2 because of utf-16
            if(pos < self.firstPos):
                self.firstPos = pos
            strData = xorCrypt(data[pos:pos + strEntry.length * 2], i)
            content.append(strData.decode("utf-16-le"))
        self.stringList = content
        self.__stringCount__ = len(self.stringList)

    def dump(self):
        base = bytearray(self.data[:self.firstPos] if(self.hasSignature()) else self.data)
        offsetTable = Entry(base[0xC:0xC + 8])
        assert(self.__stringCount__ == offsetTable.length)
        assert(len(self.stringList) == self.__stringCount__)

        base[0x14:0x14 + 4] = struct.pack("<I", len(base))
        stream = io.BytesIO()
        iTotal = 0
        for i, s in enumerate(self.stringList):
            offset = offsetTable.pos + i * 8
            base[offset:offset + 8] = Entry.pack(iTotal, len(s))
            stream.write(xorCrypt(s.encode("utf-16-le"), i))
            iTotal += len(s)
        return bytes(base + stream.getvalue() + self.signature)

    def hasSignature(self):
        return self.data[-len(self.signature):] == self.signature
