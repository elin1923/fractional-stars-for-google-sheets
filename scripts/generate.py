import math
from pathlib import Path
import struct
import zlib


STAR_SIZE = 100
PADDING = 8
GAP = 16
WIDTH = 5 * STAR_SIZE + 4 * GAP + 2 * PADDING
HEIGHT = STAR_SIZE + 2 * PADDING
SCALE = 8
GOLD = (245, 178, 26)
EMPTY = (203, 213, 225)
ROOT = Path(__file__).resolve().parents[1]


def polygon():
    points = []
    for vertex in range(10):
        angle = -math.pi / 2 + vertex * math.pi / 5
        radius = 1 if vertex % 2 == 0 else 0.46
        points.append((math.cos(angle) * radius, math.sin(angle) * radius))
    left = min(point[0] for point in points)
    right = max(point[0] for point in points)
    top = min(point[1] for point in points)
    bottom = max(point[1] for point in points)
    return [((horizontal - left) / (right - left) * STAR_SIZE * SCALE,
             (vertical - top) / (bottom - top) * STAR_SIZE * SCALE)
            for horizontal, vertical in points]


def coverage():
    points = polygon()
    counts = [[0] * STAR_SIZE for _ in range(STAR_SIZE)]
    for sample_row in range(STAR_SIZE * SCALE):
        vertical = sample_row + 0.5
        intersections = []
        for vertex, first in enumerate(points):
            second = points[(vertex + 1) % len(points)]
            if min(first[1], second[1]) <= vertical < max(first[1], second[1]):
                intersections.append(first[0] + (vertical - first[1]) *
                                     (second[0] - first[0]) / (second[1] - first[1]))
        intersections.sort()
        for pair in range(0, len(intersections), 2):
            start = max(0, math.ceil(intersections[pair] - 0.5))
            end = min(STAR_SIZE * SCALE, math.ceil(intersections[pair + 1] - 0.5))
            for sample_column in range(start, end):
                counts[sample_row // SCALE][sample_column // SCALE] += 1
    return counts


def star_rows(filled_percent, counts):
    rows = []
    for count_row in counts:
        row = bytearray()
        for column, count in enumerate(count_row):
            color = (GOLD if column < filled_percent else EMPTY) if count else (0, 0, 0)
            row.extend((*color, round(count * 255 / (SCALE * SCALE))))
        rows.append(bytes(row))
    return rows


def rating_rows(hundredths, variants):
    blank = bytes(WIDTH * 4)
    rows = [blank] * PADDING
    fills = [max(0, min(100, hundredths - position * 100)) for position in range(5)]
    for row_index in range(STAR_SIZE):
        stars = bytes(GAP * 4).join(variants[fill][row_index] for fill in fills)
        rows.append(bytes(PADDING * 4) + stars + bytes(PADDING * 4))
    return rows + [blank] * PADDING


def chunk(kind, payload):
    return (struct.pack('>I', len(payload)) + kind + payload +
            struct.pack('>I', zlib.crc32(kind + payload)))


def png(rows):
    header = struct.pack('>IIBBBBB', WIDTH, HEIGHT, 8, 6, 0, 0, 0)
    pixels = b''.join(b'\x00' + row for row in rows)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header) +
            chunk(b'IDAT', zlib.compress(pixels, 9)) + chunk(b'IEND', b''))


def main():
    target = ROOT / 'stars'
    target.mkdir(exist_ok=True)
    counts = coverage()
    variants = [star_rows(percent, counts) for percent in range(101)]
    for hundredths in range(501):
        filename = f'{hundredths // 100}.{hundredths % 100:02d}.png'
        (target / filename).write_bytes(png(rating_rows(hundredths, variants)))
    print(f'Generated 501 transparent {WIDTH} × {HEIGHT} PNGs in {target}')


if __name__ == '__main__':
    main()
