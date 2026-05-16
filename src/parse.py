import json, sqlite3
from pathlib import Path

DB = "data/clean/works.db"

def init_db():
    Path("data/clean").mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.executescript("""
        DROP TABLE IF EXISTS works;
        DROP TABLE IF EXISTS authorships;
        CREATE TABLE works (
            work_id TEXT PRIMARY KEY,
            title TEXT,
            year INTEGER,
            doi TEXT,
            primary_concept TEXT
        );
        CREATE TABLE authorships (
            work_id TEXT,
            author_id TEXT,
            author_name TEXT,
            orcid TEXT,
            institution_id TEXT,
            institution_name TEXT,
            country_code TEXT,
            author_position TEXT
        );
        CREATE INDEX idx_auth ON authorships(author_id);
        CREATE INDEX idx_country ON authorships(country_code);
        CREATE INDEX idx_year ON works(year);
    """)
    return con

def parse_all():
    con = init_db()
    n_works, n_auth = 0, 0
    for fp in sorted(Path("data/raw").glob("*.json")):
        works = json.loads(fp.read_text(encoding="utf-8"))
        for w in works:
            con.execute(
                "INSERT OR REPLACE INTO works VALUES (?,?,?,?,?)",
                (
                    w["id"],
                    w.get("title"),
                    w.get("publication_year"),
                    w.get("doi"),
                    (w.get("concepts") or [{}])[0].get("display_name"),
                ),
            )
            n_works += 1
            for a in w.get("authorships", []):
                author = a.get("author") or {}
                institutions = a.get("institutions") or [{}]
                for inst in institutions:
                    con.execute(
                        "INSERT INTO authorships VALUES (?,?,?,?,?,?,?,?)",
                        (
                            w["id"],
                            author.get("id"),
                            author.get("display_name"),
                            author.get("orcid"),
                            inst.get("id"),
                            inst.get("display_name"),
                            inst.get("country_code"),
                            a.get("author_position"),
                        ),
                    )
                    n_auth += 1
        con.commit()
        print(f"parsed {fp.name}")
    print(f"\ndone: {n_works} works, {n_auth} authorship rows")
    con.close()

if __name__ == "__main__":
    parse_all()