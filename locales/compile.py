"""
Compile all .po catalogs to .mo binaries.
Run from the project root: python locales/compile.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "cachyOs_env/lib/python3.14/site-packages"))

from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po

LOCALES_DIR = pathlib.Path(__file__).parent


def compile_catalog(lang: str) -> None:
    po_path = LOCALES_DIR / lang / "LC_MESSAGES" / "messages.po"
    mo_path = LOCALES_DIR / lang / "LC_MESSAGES" / "messages.mo"

    if not po_path.exists():
        print(f"  skipping {lang}: {po_path} not found")
        return

    with open(po_path, "rb") as f:
        catalog = read_po(f, ignore_obsolete=True)

    # strip auto-detected python-format flags — strings are passed to gettext,
    # not to %-formatting, so format checking is a false positive here
    for msg in catalog:
        msg.flags.discard("python-format")

    with open(mo_path, "wb") as f:
        write_mo(f, catalog)

    count = sum(1 for m in catalog if m.id and m.string)
    print(f"  compiled {lang}: {count} translated strings → {mo_path}")


if __name__ == "__main__":
    langs = [d.name for d in LOCALES_DIR.iterdir() if d.is_dir()]
    print(f"Compiling {len(langs)} catalogs...")
    for lang in sorted(langs):
        compile_catalog(lang)
    print("Done.")
