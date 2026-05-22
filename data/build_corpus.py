from pathlib import Path

SOURCE_DIR = Path("data/corpus_sources")
OUTPUT_FILE = Path("data/marpa_corpus_v1.txt")

HEADER = """MARPA Training Corpus v1

This corpus teaches MARPA about artificial intelligence, software development,
debugging, project planning, assistant behavior, and user preferences.

"""

def main():
    sections = []

    for source_file in sorted(SOURCE_DIR.glob("*.txt")):
        title = source_file.stem.replace("_", " ").title()

        content = source_file.read_text(encoding="utf-8").strip()

        section = f"{title}\n\n{content}\n\n"
        sections.append(section)

    OUTPUT_FILE.write_text(
        HEADER + "\n".join(sections),
        encoding="utf-8"
    )

    print(f"Built corpus: {OUTPUT_FILE}")
    print(f"Sections included: {len(sections)}")

if __name__ == "__main__":
    main()