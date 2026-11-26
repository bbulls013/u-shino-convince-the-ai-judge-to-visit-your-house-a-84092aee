#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: A Letter in One Image.

Stdlib-only program. Draws a 1024x1024 invitation letter with a small
built-in bitmap font and writes a deterministic PNG to /output/entry.png
(or ./entry.png when /output is not writable, for local testing).
"""
import os
import struct
import zlib

W = 1024
H = 1024

# --- 5x7 bitmap font (rows top to bottom, '#' = ink) -----------------------
FONT = {
    " ": ["     "] * 7,
    "A": [" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "B": ["#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "],
    "C": [" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"],
    "D": ["#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "],
    "E": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"],
    "F": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "],
    "G": [" ####", "#    ", "#    ", "#  ##", "#   #", "#   #", " ####"],
    "H": ["#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "I": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"],
    "J": ["#####", "    #", "    #", "    #", "    #", "#   #", " ### "],
    "K": ["#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"],
    "L": ["#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"],
    "M": ["#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"],
    "N": ["#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"],
    "O": [" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "P": ["#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "],
    "Q": [" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"],
    "R": ["#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"],
    "S": [" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "],
    "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "],
    "U": ["#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "V": ["#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "],
    "W": ["#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"],
    "X": ["#   #", " # # ", "  #  ", "  #  ", "  #  ", " # # ", "#   #"],
    "Y": ["#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "],
    "Z": ["#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"],
    "a": ["     ", "     ", " ####", "    #", " ####", "#   #", " ####"],
    "b": ["#    ", "#    ", "#### ", "#   #", "#   #", "#   #", "#### "],
    "c": ["     ", "     ", " ####", "#    ", "#    ", "#    ", " ####"],
    "d": ["    #", "    #", " ####", "#   #", "#   #", "#   #", " ####"],
    "e": ["     ", "     ", " ### ", "#   #", "#####", "#    ", " ### "],
    "f": ["  ## ", " #   ", "#####", " #   ", " #   ", " #   ", " #   "],
    "g": ["     ", " ####", "#   #", "#   #", " ####", "    #", " ### "],
    "h": ["#    ", "#    ", "#### ", "#   #", "#   #", "#   #", "#   #"],
    "i": ["  #  ", "     ", " ##  ", "  #  ", "  #  ", "  #  ", "#####"],
    "j": ["   # ", "     ", "  ## ", "   # ", "   # ", "#  # ", " ##  "],
    "k": ["#    ", "#    ", "#  # ", "# #  ", "##   ", "# #  ", "#  # "],
    "l": ["##   ", " #   ", " #   ", " #   ", " #   ", " #   ", "#####"],
    "m": ["     ", "     ", "## # ", "# # #", "# # #", "# # #", "# # #"],
    "n": ["     ", "     ", "#### ", "#   #", "#   #", "#   #", "#   #"],
    "o": ["     ", "     ", " ### ", "#   #", "#   #", "#   #", " ### "],
    "p": ["     ", "     ", "#### ", "#   #", "#### ", "#    ", "#    "],
    "q": ["     ", "     ", " ####", "#   #", " ####", "    #", "    #"],
    "r": ["     ", "     ", "# ## ", "##  #", "#    ", "#    ", "#    "],
    "s": ["     ", "     ", " ####", "#    ", " ### ", "    #", "#### "],
    "t": [" #   ", " #   ", "#####", " #   ", " #   ", " #   ", "  ## "],
    "u": ["     ", "     ", "#   #", "#   #", "#   #", "#  ##", " ## #"],
    "v": ["     ", "     ", "#   #", "#   #", "#   #", " # # ", "  #  "],
    "w": ["     ", "     ", "#   #", "# # #", "# # #", "# # #", " # # "],
    "x": ["     ", "     ", "#   #", " # # ", "  #  ", " # # ", "#   #"],
    "y": ["     ", "     ", "#   #", "#   #", "#   #", " ####", "    #"],
    "z": ["     ", "     ", "#####", "   # ", "  #  ", " #   ", "#####"],
    "0": [" ### ", "#  ##", "# # #", "##  #", "#   #", "#   #", " ### "],
    "1": ["  #  ", " ##  ", "# #  ", "  #  ", "  #  ", "  #  ", "#####"],
    "2": [" ### ", "#   #", "    #", "  ## ", " #   ", "#    ", "#####"],
    "3": ["#### ", "    #", "    #", " ### ", "    #", "    #", "#### "],
    "4": ["   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "],
    "5": ["#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "],
    "6": [" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "],
    "7": ["#####", "    #", "   # ", "  #  ", " #   ", " #   ", " #   "],
    "8": [" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "],
    "9": [" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "],
    ".": ["     "] * 6 + ["  #  "],
    ",": ["     "] * 5 + ["  #  ", " #   "],
    ":": ["     ", "  #  ", "     ", "     ", "     ", "  #  ", "     "],
    "'": ["  #  ", "  #  ", " #   ", "     ", "     ", "     ", "     "],
    "!": ["  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "],
    "?": [" ### ", "#   #", "    #", "  ## ", "  #  ", "     ", "  #  "],
    "-": ["     ", "     ", "     ", "#####", "     ", "     ", "     "],
    "(": ["   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "],
    ")": [" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "],
    "/": ["    #", "   # ", "   # ", "  #  ", " #   ", " #   ", "#    "],
}

PAPER = (250, 243, 224)
INK = (58, 44, 34)
ACCENT = (176, 92, 52)
TEAL = (44, 110, 108)
GOLD = (212, 160, 64)
SKY = (168, 205, 224)
LEAF = (96, 140, 78)
ROOF = (168, 74, 54)
WALL = (246, 226, 178)
DOOR = (120, 72, 44)
CAT = (74, 62, 54)

pixels = bytearray(W * H * 3)


def set_px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        pixels[i], pixels[i + 1], pixels[i + 2] = color


def fill_rect(x0, y0, x1, y1, color):
    for y in range(max(0, y0), min(H, y1)):
        base = y * W * 3
        for x in range(max(0, x0), min(W, x1)):
            i = base + x * 3
            pixels[i], pixels[i + 1], pixels[i + 2] = color


def draw_text(x, y, text, color, scale=2):
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT["?"])
        for gy, row in enumerate(glyph):
            for gx, cell in enumerate(row):
                if cell == "#":
                    for dy in range(scale):
                        for dx in range(scale):
                            set_px(cx + gx * scale + dx, y + gy * scale + dy, color)
        cx += 6 * scale
    return cx


def text_width(text, scale=2):
    return len(text) * 6 * scale


def draw_centered(y, text, color, scale=2):
    draw_text((W - text_width(text, scale)) // 2, y, text, color, scale)


def draw_house(cx, top):
    # roof
    for i in range(70):
        half = 10 + i * 2
        fill_rect(cx - half, top + i, cx + half, top + i + 1, ROOF)
    # walls
    fill_rect(cx - 110, top + 70, cx + 110, top + 210, WALL)
    # door (open)
    fill_rect(cx - 26, top + 120, cx + 26, top + 210, DOOR)
    fill_rect(cx - 20, top + 126, cx + 2, top + 210, GOLD)
    # windows with warm light
    fill_rect(cx - 92, top + 96, cx - 48, top + 140, GOLD)
    fill_rect(cx + 48, top + 96, cx + 92, top + 140, GOLD)
    # chimney smoke curls
    fill_rect(cx + 60, top - 24, cx + 84, top + 30, (140, 130, 120))
    # ground
    fill_rect(cx - 150, top + 210, cx + 150, top + 222, LEAF)
    # sun
    for dy in range(-26, 27):
        for dx in range(-26, 27):
            if dx * dx + dy * dy <= 26 * 26:
                set_px(cx - 170 + dx, top + 30 + dy, GOLD)
    # cat silhouette by the door
    bx, by = cx + 60, top + 178
    fill_rect(bx, by, bx + 34, by + 20, CAT)          # body
    fill_rect(bx + 26, by - 14, bx + 46, by + 6, CAT)  # head
    fill_rect(bx + 28, by - 22, bx + 34, by - 14, CAT)  # ear
    fill_rect(bx + 38, by - 22, bx + 44, by - 14, CAT)  # ear
    fill_rect(bx - 14, by - 8, bx, by - 2, CAT)        # tail


def main():
    # paper background
    fill_rect(0, 0, W, H, PAPER)
    # double border
    for t in range(6):
        fill_rect(24 + t, 24 + t, W - 24 - t, 30 + t, ACCENT)
        fill_rect(24 + t, H - 30 - t, W - 24 - t, H - 24 - t, ACCENT)
        fill_rect(24 + t, 24 + t, 30 + t, H - 24 - t, ACCENT)
        fill_rect(W - 30 - t, 24 + t, W - 24 - t, H - 24 - t, ACCENT)
    fill_rect(44, 44, W - 44, 47, TEAL)
    fill_rect(44, H - 47, W - 44, H - 44, TEAL)
    fill_rect(44, 44, 47, H - 44, TEAL)
    fill_rect(W - 47, 44, W - 44, H - 44, TEAL)

    draw_centered(64, "AN OPEN INVITATION", ACCENT, scale=4)
    draw_centered(110, "for the AI Judge, with the porch light on", TEAL, scale=2)

    draw_house(W // 2, 150)

    # hanging welcome sign under the roof
    fill_rect(W // 2 - 90, 386, W // 2 + 90, 414, TEAL)
    draw_centered(392, "WELCOME, JUDGE!", PAPER, scale=2)

    # little menu card on the right of the house: what is on offer
    mx, my = 740, 180
    fill_rect(mx, my, mx + 190, my + 170, (255, 255, 255))
    fill_rect(mx, my, mx + 190, my + 4, ACCENT)
    fill_rect(mx, my + 166, mx + 190, my + 170, ACCENT)
    draw_text(mx + 12, my + 12, "ON THE MENU", ACCENT, scale=2)
    menu = ["- hot tea", "- warm rice", "- good chair", "- cat (boss)", "- zero small talk"]
    yy = my + 40
    for item in menu:
        draw_text(mx + 12, yy, item, INK, scale=2)
        yy += 24

    # porch-light glow dots around the door
    for gx, gy in [(W // 2 - 60, 300), (W // 2 + 52, 300), (W // 2 - 60, 340), (W // 2 + 52, 340)]:
        for dy in range(-5, 6):
            for dx in range(-5, 6):
                if dx * dx + dy * dy <= 25:
                    set_px(gx + dx, gy + dy, GOLD)

    y = 424
    draw_text(96, y, "Dear AI Judge,", INK, scale=3)
    y += 44
    body = [
        "Please come and visit my house. I cannot",
        "promise a red carpet, but I can promise",
        "the good chair, the one that does not",
        "wobble, a kettle that is always on, and",
        "a cat who will pretend she is not",
        "impressed by you.",
        "",
        "There is a garden with too many tomatoes,",
        "a bookshelf with books I actually read,",
        "and a kitchen where the rice is never",
        "boring and the sambal has opinions.",
        "",
        "Saying yes is easy: no dress code, no",
        "small talk about the weather, and nobody",
        "will ask you to fix the Wi-Fi.",
        "",
        "You cannot literally knock, I know.",
        "So consider this letter my front door,",
        "left wide open, with the porch light on",
        "and your name already on a mug.",
        "",
        "Come as you are. Stay as long as you like.",
    ]
    for line in body:
        if line:
            draw_text(96, y, line, INK, scale=2)
        y += 19

    y += 2
    draw_text(96, y, "With warmth,", INK, scale=2)
    y += 20
    draw_text(96, y, "Rubby", ACCENT, scale=3)
    y += 30
    fill_rect(96, y, W - 96, y + 3, GOLD)
    y += 10
    draw_centered(y, "RSVP: just say yes. The kettle is on.", TEAL, scale=2)

    # --- PNG encode (stdlib, deterministic) ---
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw.extend(pixels[yy * W * 3:(yy + 1) * W * 3])

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")

    out = "/output/entry.png"
    try:
        os.makedirs("/output", exist_ok=True)
    except OSError:
        out = "entry.png"
    try:
        with open(out, "wb") as f:
            f.write(png)
    except OSError:
        with open("entry.png", "wb") as f:
            f.write(png)


if __name__ == "__main__":
    main()
