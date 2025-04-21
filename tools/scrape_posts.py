import json
import os
import time

import requests
from bs4 import BeautifulSoup


def scrape_blogspot(blog_url, max_pages=None, output_file="blogspot_posts.json"):
    """
    Scrape posts from a Blogspot blog and save to a single JSON file

    Args:
        blog_url: URL of the blogspot blog (e.g., 'https://example.blogspot.com')
        max_pages: Maximum number of pages to scrape (None for all)
        output_file: File to save the scraped posts
    """
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    page_num = 1
    has_next = True
    all_posts = []

    # Fix URL formatting - remove quotes and ensure proper format
    blog_url = blog_url.strip("\"'")

    # Ensure URL has proper http/https prefix
    if not blog_url.startswith(("http://", "https://")):
        blog_url = "https://" + blog_url

    # Remove trailing slash if present
    if blog_url.endswith("/"):
        blog_url = blog_url[:-1]

    print(f"Starting to scrape: {blog_url}")

    # Start with the main URL
    next_page_url = blog_url

    while has_next and (max_pages is None or page_num <= max_pages):
        print(f"Scraping page {page_num}: {next_page_url}")

        # Send request with a user agent to avoid being blocked
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(next_page_url, headers=headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Find all blog posts on the page
            posts = (
                soup.select(".post") or soup.select(".hentry") or soup.select("article")
            )

            if not posts:
                print(
                    f"No posts found on this page. Check the blog structure. URL: {next_page_url}"
                )
                print("Trying alternative selectors...")

                # Try some alternative selectors that might work with different Blogspot themes
                posts = (
                    soup.select(".blog-post")
                    or soup.select(".blog-posts > div")
                    or soup.select(".entry")
                )

                if not posts:
                    print("Still no posts found. Breaking.")
                    break

            print(f"Found {len(posts)} posts on page {page_num}")

            # Process each post
            for post in posts:
                post_data = {}

                # Extract title (try multiple possible selectors)
                title_elem = (
                    post.select_one(".post-title")
                    or post.select_one("h3.entry-title")
                    or post.select_one("h2.entry-title")
                    or post.select_one("h1.entry-title")
                    or post.select_one(".entry-header h2")
                    or post.select_one("h2 a")
                )

                if title_elem and hasattr(title_elem, "a") and title_elem.a:
                    post_data["title"] = title_elem.a.text.strip()
                    post_data["url"] = title_elem.a.get("href", "")
                elif title_elem:
                    post_data["title"] = title_elem.text.strip()
                    # Look for links in the title element
                    link = title_elem.find("a")
                    post_data["url"] = link.get("href", "") if link else ""
                else:
                    post_data["title"] = "Untitled Post"
                    post_data["url"] = ""

                # Extract publication date (try multiple possible selectors)
                date_elem = (
                    post.select_one(".date-header")
                    or post.select_one(".published")
                    or post.select_one(".post-timestamp")
                    or post.select_one(".date-outer")
                    or post.select_one(".post-meta")
                )
                post_data["date"] = (
                    date_elem.text.strip() if date_elem else "Unknown Date"
                )

                # Extract content (try multiple possible selectors)
                content_elem = (
                    post.select_one(".post-body")
                    or post.select_one(".entry-content")
                    or post.select_one(".post-entry")
                    or post.select_one(".post-content")
                )
                post_data["content"] = content_elem.text.strip() if content_elem else ""

                # Extract comments count if available
                comments_elem = post.select_one(".comment-link")
                post_data["comments_count"] = (
                    comments_elem.text.strip() if comments_elem else "0"
                )

                # Add post ID if we can extract it
                if post.get("id"):
                    post_data["id"] = post["id"]

                # Skip if we already have this post (check by URL or title)
                if any(
                    p.get("url") == post_data.get("url") and post_data.get("url")
                    for p in all_posts
                ) or any(
                    p.get("title") == post_data.get("title")
                    and post_data.get("title") != "Untitled Post"
                    for p in all_posts
                ):
                    print(f"Skipping duplicate post: {post_data.get('title')}")
                    continue

                all_posts.append(post_data)

            # Find the "Older Posts" link - Blogspot uses several possible formats
            next_link = None

            # Method 1: Look for the older posts link
            older_links = soup.select(
                "a.blog-pager-older-link, #Blog1_blog-pager-older-link, .blog-pager-older-link"
            )
            if older_links:
                next_link = older_links[0]

            # Method 2: Look for the next page link in the pagination
            if not next_link:
                pagination = soup.select(".blog-pager a, .pagination a")
                for link in pagination:
                    if link.text.strip().lower() in [
                        "older",
                        "older posts",
                        "previous",
                        "›",
                        "»",
                        "next",
                        "older entries",
                    ]:
                        next_link = link
                        break

            # Check if we found a next page link
            if next_link and next_link.get("href"):
                next_page_url = next_link["href"]
                has_next = True
                print(f"Next page URL: {next_page_url}")
            else:
                has_next = False
                print("No next page found.")

            # Save progress so far to the file after each page
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(all_posts, f, ensure_ascii=False, indent=4)

            page_num += 1

            # Be nice to the server
            time.sleep(2)

        except Exception as e:
            print(f"Error scraping page {page_num}: {str(e)}")
            print(f"Current URL: {next_page_url}")
            break

    print(f"Scraping completed. Scraped {len(all_posts)} posts to {output_file}")
    return all_posts


if __name__ == "__main__":
    try:
        # Example usage
        blog_url = input(
            "Enter the Blogspot URL (e.g., https://example.blogspot.com): "
        )
        max_pages = input(
            "Enter maximum number of pages to scrape (leave empty for all): "
        )
        output_file = (
            input("Enter output file path (default: blogspot_posts.json): ")
            or "blogspot_posts.json"
        )

        max_pages = int(max_pages) if max_pages.strip() else None

        scrape_blogspot(blog_url, max_pages, output_file)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
