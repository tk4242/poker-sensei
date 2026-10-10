"""オリジナルのドット絵（16×16）を SVG にする。既存ゲームの素材は使っていない（このファイルの文字の絵が原本）。

使い方: python3 app/sprites/make_sprites.py  → app/sensei/static/sprites/*.svg を作り直す
"""
from pathlib import Path

PAL = {
    "k": "#1a1a2e", "w": "#ffffff", "s": "#f2c18d", "r": "#d83a3a", "b": "#3a6fd8", "B": "#24408a",
    "g": "#3fae4a", "G": "#23702c", "y": "#f5d33f", "o": "#e8852b", "p": "#8a4fd0", "P": "#5a2d91",
    "n": "#8b5a2b", "N": "#5c3a1a", "e": "#a8adb3", "E": "#5f6368", "c": "#6fd6e8", "m": "#f08ab0",
}

SPRITES = {
    "hero": [
        "......kkkk......", "....kkbbbbkk....", "...kbbbbbbbbk...", "...krrrrrrrrk...",
        "...kssssssssk...", "...kssksskssk...", "...kssssssssk...", "....kssrrssk....",
        ".....kkkkkk.....", "...kbbbbbbbbk...", "..kbbbyyyybbbk..", "..kskbbbbbbksk..",
        "..kkkbbbbbbkkk..", "....knnnnnnk....", "....knnkknnk....", "...kkkk..kkkk...",
    ],
    "sensei": [
        ".......kk.......", "......kppk......", ".....kppppk.....", ".....kpypPk.....",
        "....kppppppk....", "..kkkkkkkkkkkk..", "....kssssssk....", "....kskssksk....",
        "....kwwsswwk....", "...kwwwwwwwwk...", "..kpkwwwwwwkpk..", "..kppkwwwwkppk..",
        "..kpppkwwkpppk..", "..kppppppppppk..", "..kppppppppppk..", "...kkkkkkkkkk...",
    ],
    "ghost": [
        "......kkkk......", "....kkwwwwkk....", "...kwwwwwwwwk...", "..kwwwwwwwwwwk..",
        "..kwwkkwwkkwwk..", "..kwwkkwwkkwwk..", "..kwwwwwwwwwwk..", "..kwwwwkkwwwwk..",
        "..kwwwkmmkwwwk..", ".kwwwwwwwwwwwwk.", "kwwkwwwwwwwwkwwk", ".kkkwwwwwwwwkkk.",
        "...kwwwwwwwwk...", "...kwwkwwkwwk...", "...kwk.kk.kwk...", "....k......k....",
    ],
    "bat": [
        "................", "................", "................", "................",
        "kk....kkkk....kk", "kpk..kppppk..kpk", "kppkkpyppypkkppk", "kppppppppppppppk",
        "kpPpppkwwkpppPpk", ".kPpPppppppPpPk.", "..kPk.kppk.kPk..", "...k...kk...k...",
        "................", "................", "................", "................",
    ],
    "knight": [
        ".......rr.......", "......rrr.......", "......kkkk......", ".....keeeek.....",
        "....keeeeeek....", "....kkkkkkkk....", "....keykkyek....", "....keeeeeek....",
        ".....kkkkkk.....", "..kkeeeeeeeekk..", ".kekeeeyyeeekek.", ".kekeeeeeeeekek.",
        ".kskkeeeeeekksk.", "....keeEEeek....", "....keek.keek...", "...kkkk..kkkk...",
    ],
    "goblin": [
        "................", "................", "..k..........k..", "..kgk.kkkk.kgk..",
        "..kggkggggkggk..", "...kggggggggk...", "...kgyyggyygk...", "...kggggggggk...",
        "...kgkwwwwkgk...", "....kggggggk....", "..kkknnnnnnkkk..", ".kgknnyynnnkgk..",
        ".kgknnnnnnnkgk..", "...kgggggggk....", "...kggk.kggk....", "..kkkk..kkkk....",
    ],
    "golem": [
        "................", "....kkkkkkkk....", "...keeeeeeeek...", "...keEeeeeEek...",
        "...kekkeekkek...", "...keeeeeeeek...", "...keeEEEEeek...", ".kkkkeeeeeekkkk.",
        "keeeekEeeEkeeeek", "keEeekeeeekeeEek", "keeeekeEEeekeeek", "kkkkkeeeeeekkkkk",
        "....keeGeeek....", "....keek.keek...", "...keeek.keeek..", "...kkkkk.kkkkk..",
    ],
    "ogre": [
        "..k..........k..", "..kyk......kyk..", "...kyk.kk.kyk...", "....kkrrrrkk....",
        "...krrrrrrrrk...", "...krwkrrwkrk...", "...krrrrrrrrk...", "...krkwkkwkrk...",
        "....krrrrrrk....", ".kkkknnnnnnkkkk.", "krrrknnnnnnkrrrk", "krrkknnnnnnkkrrk",
        "kssk.krrrrk.kssk", "kkk..krrrrk..kkk", ".....krkkrk.....", "....kkk..kkk....",
    ],
    "dragon": [
        "..........kk....", ".........kbbk...", "........kbbbbk..", "........kbwkbk..",
        "...kk...kbbbbbk.", "..kbbk.kbbbbbkk.", ".kbbbbkkbbbbk...", "kbbkbbbkbbbk....",
        "kbk.kbbbyybbk...", "kk..kbbyyyybbk..", "...kbbbyyyybbk..", "...kbbbbyybbbk..",
        "....kbbbbbbbbkk.", "....kbbk.kbbkbbk", "...kkkk..kkkk.kk", "................",
    ],
    "mimic": [
        "................", "................", "..kkkkkkkkkkkk..", ".knnwknnnnwknnk.",
        ".knNNnnnnnnNNnk.", ".kyyyyyyyyyyyyk.", ".kwkwkwkwkwkwkk.", ".kkkkkrrrrkkkkk.",
        ".kkwkwkwkwkwkwk.", ".kyyyyyyyyyyyyk.", ".knnnnnyynnnnnk.", ".knNnnnyynnnNnk.",
        ".knnnnnnnnnnnnk.", ".kkkkkkkkkkkkkk.", "................", "................",
    ],
}


def to_svg(rows):
    assert len(rows) == 16 and all(len(r) == 16 for r in rows), [len(r) for r in rows]
    rects = []
    for y, row in enumerate(rows):
        x = 0
        while x < 16:
            ch = row[x]
            if ch == ".":
                x += 1
                continue
            end = x
            while end < 16 and row[end] == ch:
                end += 1
            rects.append(f'<rect x="{x}" y="{y}" width="{end - x}" height="1" fill="{PAL[ch]}"/>')
            x = end
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" shape-rendering="crispEdges">'
            + "".join(rects) + "</svg>\n")


def main():
    out = Path(__file__).resolve().parents[1] / "sensei" / "static" / "sprites"
    out.mkdir(parents=True, exist_ok=True)
    for name, rows in SPRITES.items():
        (out / f"{name}.svg").write_text(to_svg(rows), encoding="utf-8")
    print(f"{len(SPRITES)} sprites -> {out}")


if __name__ == "__main__":
    main()
