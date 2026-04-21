import re
import requests
import argparse
from bs4 import BeautifulSoup

# ----------------------------------------
# Function: Extract song title and author
# ----------------------------------------
def get_song_info(url):
    """Return (title, author) from supported guitar/tab sites"""
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # topaccords.com
        if "topaccords.com" in url:
            title = soup.find("h1").text.strip()
            author = soup.find("h2").text.strip()

        # boiteachansons.net
        elif "boiteachansons.net" in url:
            header = soup.find("h1").text.strip()
            parts = header.split(" - ")
            if len(parts) == 2:
                author, title = parts
            else:
                title = header
                author = "Inconnu"

        # ultimate-guitar.com
        elif "ultimate-guitar.com" in url:
            title_tag = soup.find("meta", property="og:title")
            title = title_tag["content"] if title_tag else "Unknown Title"
            if " by " in title:
                title, author = title.split(" by ")
                title = title.replace(" chords", "").strip()
            else:
                author = "Unknown"

        else:
            return ("Unknown Title", "Unknown")

        return (title.strip(), author.strip())

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ("Unknown Title", "Unknown")

# ----------------------------------------
# Main function to update the markdown file
# ----------------------------------------
def update_markdown_table(input_file):
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    updated_lines = []
    header_processed = False

    for idx, line in enumerate(lines):
        # Insert "Auteur" as second column in header
        if not header_processed and line.strip().startswith("|"):
            columns = [col.strip() for col in line.strip().split("|") if col.strip()]
            if "Auteur" not in columns:
                columns.insert(1, "Auteur")
                updated_header = "| " + " | ".join(columns) + " |\n"
                updated_lines.append(updated_header)

                # Separator line
                sep_parts = ["--------"] * len(columns)
                updated_lines.append("| " + " | ".join(sep_parts) + " |\n")
                header_processed = True
                continue  # Skip next line (separator)
            else:
                updated_lines.append(line)
                header_processed = True
                continue

        # Process lines with a Markdown link
        match = re.search(r"\((https?://[^\s)]+)\)", line)
        if match:
            url = match.group(1)
            title, author = get_song_info(url)
            markdown_link = f"[{title}]({url})"

            # Parse the line into columns
            parts = [col.strip() for col in line.strip().split("|") if col.strip()]
            if len(parts) >= 2:
                parts[0] = markdown_link
                parts.insert(1, author)
                line = "| " + " | ".join(parts) + " |\n"

        updated_lines.append(line)

    # Save the updated Markdown file
    with open(input_file, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)

    print(f"Table updated successfully in '{input_file}'")

# ----------------------------------------
# Command-line interface using argparse
# ----------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Update a Markdown table of songs with clickable titles and author names from guitar/tab websites."
    )
    parser.add_argument(
        "-i", "--input",
        help="Path to the Markdown file to update",
        default="jam_table.md"
    )

    args = parser.parse_args()
    update_markdown_table(args.input)

if __name__ == "__main__":
    main()
