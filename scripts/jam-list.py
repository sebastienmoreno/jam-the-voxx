import re
from pathlib import Path
from urllib.parse import urlparse

def extract_song_info(url):
    path = urlparse(url).path.strip("/")
    parts = path.split("/")

    if len(parts) < 2:
        return None

    artiste = parts[-2]
    titre = parts[-1]

    # nettoyage
    artiste = artiste.replace("-", " ").title()
    titre = titre.replace("-", " ").title()

    return titre, artiste, url


def extract_urls(file_path):
    content = Path(file_path).read_text(encoding="utf-8")
    return re.findall(r"https?://[^\s\]]+", content)


def main():
    files = Path(".").glob("jam-*.md")

    songs = []

    for file in files:
        if file.name == "jam-the-voxx.md":
            continue

        urls = extract_urls(file)
        for url in urls:
            info = extract_song_info(url)
            if info:
                songs.append(info)

    # suppression des doublons
    songs = list(set(songs))

    # tri par titre
    songs.sort(key=lambda x: x[0])

    # génération du markdown
    output = []
    output.append("| Titre | Artiste | Lien |")
    output.append("|------|---------|------|")

    for titre, artiste, url in songs:
        output.append(f"| {titre} | {artiste} | [{titre}]({url}) |")

    Path("jam-the-voxx.md").write_text("\n".join(output), encoding="utf-8")


if __name__ == "__main__":
    main()
