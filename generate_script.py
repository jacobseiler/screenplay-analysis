import html2text
import re
import requests


def scrape_html_and_save(url, fname_out):

    # Set some options for parsing the HTML to text.
    parser = html2text.HTML2Text()
    parser.unicode_snob = True
    parser.body_width = 0
    parser.skip_internal_links = True
    parser.ignore_links = True

    # Now get the HTML page.
    r = requests.get(url)
    if r.status_code != 200:
        print(f"Encountered error while fetching webpage {url}")
        raise RuntimeError

    # Snip out all that HTML nonsense and leave just the text (this will be the script
    # itself).
    data = r.text
    text = parser.handle(data)

    with open(fname_out, "w") as f:
        f.write(text)
    print(f"Saved to {fname_out}")



def generate_episode_names(url, fname_out):

    # First scrape the URL and turn the ugly HTML to nicely formatted text.
    scrape_html_and_save(url, fname_out)

    # The episode names are on lines as "### <Episode Name> Lyrics".

    with open(fname_out, "r") as f:
        for line in f:

            # Ignore empty lines.
            try:
                _ = (line.split())[0]
            except IndexError:
                continue

            reg_exp = re.compile(r"###. ([A-Z].*)Lyrics", re.IGNORECASE)
            reg_line = reg_exp.split(line)  # Split on this search.
            print(f"Line {line}")
            print(f"Reg_line {reg_line}")

    exit()

    return episode_names


def generate_script(url, save_path):

    text = scrape_html_to_text(url)

    # Now save the trimmed text.
    fname_out = "{0}/s01e02.txt".format(save_path)
    with open(fname_out, "w") as f:
        f.write(text)
    print(f"Saved to {fname_out}")



if __name__ == "__main__":

    #url = "https://genius.com/Game-of-thrones-the-kingsroad-annotated"
    url = "https://genius.com/albums/Game-of-thrones/Season-1-scripts"
    fname_out = "/home/jseiler/screenplay-analysis/scripts/season-1-episodes.txt"
    generate_episode_names(url, fname_out)
    save_path = "/home/jseiler/screenplay-analysis/scripts"
    #generate_script(url, save_path)
