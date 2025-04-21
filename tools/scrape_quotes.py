import argparse
import json
import re


def extract_fancy_nancy_sayings(input_file, output_file=None):
    """
    Extract all "Fancy Nancy Says:" quotes from the posts and save them to a new JSON file.

    Args:
        input_file: Path to the input JSON file with blog posts
        output_file: Path to save the extracted quotes (default is 'fancy_nancy_sayings.json')
    """
    if output_file is None:
        output_file = "fancy_nancy_sayings.json"

    try:
        # Read the input JSON file
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # List to store Fancy Nancy sayings
        sayings = []

        # Regular expression to match "Fancy Nancy Says:" and variations
        pattern = re.compile(
            r"(?:Fancy Nancy Says:|Fnacy Nancy Says:|Famcy Nancy Says:|Fancy Nancy Says;|Fancyr Nancy Says:)[:\s]*(.*?)(?:\n|$)",
            re.IGNORECASE,
        )

        # Extract sayings from each post
        for post in data:
            # Get the post content
            content = post.get("content", "")
            date = post.get("date", "")

            # Try to parse the date (assuming it's in the format '6:11 PM')
            post_datetime = None
            try:
                # If the date field just has time like "6:11 PM", we'll use it as is
                post_datetime = date
            except:
                post_datetime = date

            # Find all Fancy Nancy sayings in the post content
            matches = pattern.findall(content)

            # Add each saying to the list with metadata
            for saying in matches:
                if saying.strip():  # Skip empty sayings
                    saying_data = {
                        "saying": saying.strip(),
                        "post_title": post.get("title", "Untitled"),
                        "post_date": post_datetime,
                        "post_url": post.get("url", ""),
                    }
                    sayings.append(saying_data)

        # Save the sayings to a JSON file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(sayings, f, ensure_ascii=False, indent=4)

        print(
            f"Successfully extracted {len(sayings)} Fancy Nancy sayings to {output_file}"
        )
        return sayings

    except Exception as e:
        print(f"Error processing the file: {str(e)}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Extract Fancy Nancy sayings from blog posts"
    )
    parser.add_argument(
        "input_file", help="Path to the input JSON file with blog posts"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Path to save the extracted quotes (default: fancy_nancy_sayings.json)",
    )

    args = parser.parse_args()

    extract_fancy_nancy_sayings(args.input_file, args.output)


if __name__ == "__main__":
    main()
