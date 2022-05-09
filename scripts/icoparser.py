# coding = utf-8

import struct
from typing import List, Union

ICO_FORMAT = r"<BBBBHHII"


class InvalidFormatException(Exception):
    pass


class Ico(object):
    def __init__(self, ico_bytes: Union[bytes, bytearray], offset: int):
        w, h, nc, _, np, bpp, img_len, ofs = struct.unpack_from(ICO_FORMAT, ico_bytes, offset)
        self.width = w
        self.height = h
        self.color_depth = nc
        self.plane_count = np
        self.bpp = bpp
        self.ofs = ofs
        self.image = ico_bytes[self.ofs:self.ofs + img_len]

    def build_header(self) -> bytes:
        return struct.pack(ICO_FORMAT,
                           self.width,
                           self.height,
                           self.color_depth,
                           0,
                           self.plane_count,
                           self.bpp,
                           len(self.image),
                           self.ofs)


class IcoParser(object):
    def __init__(self, img_entries: List[Ico]):
        self.images = img_entries

    @staticmethod
    def parse(ico_data: Union[bytes, bytearray]):
        # ICONDIR
        if ico_data[0:4] != b"\x00\x00\x01\x00":
            raise InvalidFormatException()
        num_images, = struct.unpack_from('<H', ico_data, 4)
        if not num_images:
            raise InvalidFormatException()

        # parse every individual icons
        img_list = []
        offset = 6
        for idx in range(0, num_images):
            img = Ico(ico_data, offset)
            img_list.append(img)
            offset += struct.calcsize(ICO_FORMAT)
        return IcoParser(img_list)

    def build(self) -> bytes:
        if not self.images:
            return b''
        # ICONDIR
        data = b"\x00\x00\x01\x00" + struct.pack('<H', len(self.images))
        # fix image data offset
        fix_ofs = len(data) + struct.calcsize(ICO_FORMAT) * len(self.images)
        for img in self.images:
            img.ofs = fix_ofs
            fix_ofs += len(img.image)
        # fill headers
        for img in self.images:
            data += img.build_header()
        # fill image data
        for img in self.images:
            data += img.image
        return data
