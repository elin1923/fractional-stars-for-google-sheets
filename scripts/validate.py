import hashlib
from pathlib import Path
import struct
import zlib


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 580
HEIGHT = 116
GOLD = bytes((245, 178, 26))
EMPTY = bytes((203, 213, 225))


def decode(path):
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', path
    offset = 8
    compressed = bytearray()
    while offset < len(data):
        length = struct.unpack('>I', data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + length]
        checksum = struct.unpack('>I', data[offset + 8 + length:offset + 12 + length])[0]
        assert zlib.crc32(kind + payload) == checksum, path
        if kind == b'IHDR':
            assert struct.unpack('>IIBBBBB', payload) == (WIDTH, HEIGHT, 8, 6, 0, 0, 0), path
        if kind == b'IDAT':
            compressed.extend(payload)
        offset += length + 12
    assert kind == b'IEND' and offset == len(data), path
    raw = zlib.decompress(compressed)
    stride = WIDTH * 4 + 1
    assert len(raw) == stride * HEIGHT, path
    assert all(raw[row * stride] == 0 for row in range(HEIGHT)), path
    return b''.join(raw[row * stride + 1:(row + 1) * stride] for row in range(HEIGHT))


def main():
    expected = {f'{rating // 100}.{rating % 100:02d}.png' for rating in range(501)}
    assert {path.name for path in (ROOT / 'stars').glob('*.png')} == expected
    baseline = decode(ROOT / 'stars' / '0.00.png')
    alpha = baseline[3::4]
    assert 0 in alpha and 255 in alpha and any(0 < value < 255 for value in alpha)
    hashes = set()
    previous_gold = -1
    for rating in range(501):
        path = ROOT / 'stars' / f'{rating // 100}.{rating % 100:02d}.png'
        pixels = decode(path)
        assert pixels[3::4] == alpha, path
        hashes.add(hashlib.sha256(pixels).digest())
        gold_coverage = 0
        for vertical in range(HEIGHT):
            for horizontal in range(WIDTH):
                offset = (vertical * WIDTH + horizontal) * 4
                if not pixels[offset + 3]:
                    continue
                position, column = divmod(horizontal - 8, 116)
                assert 0 <= position < 5 and 0 <= column < 100, path
                fill = max(0, min(100, rating - position * 100))
                expected_color = GOLD if column < fill else EMPTY
                assert pixels[offset:offset + 3] == expected_color, (path, horizontal, vertical)
                if expected_color == GOLD:
                    gold_coverage += pixels[offset + 3]
        assert gold_coverage > previous_gold, path
        previous_gold = gold_coverage
    assert len(hashes) == 501
    print('Passed: 501 unique PNGs, valid CRCs, 580 × 116 RGBA, consistent transparency,')
    print('antialiased edges, exact fractional clipping and strictly increasing gold coverage.')


if __name__ == '__main__':
    main()
