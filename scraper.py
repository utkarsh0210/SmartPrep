# scraper.py
import requests
from bs4 import BeautifulSoup
import re

def scrape_nptel_course(url: str):
    """Generic scraper for any NPTEL course."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title_tag = soup.find('h1') or soup.find('title')
        course_title = title_tag.get_text(strip=True).split('|')[0].strip() if title_tag else "Unknown NPTEL Course"

        instructors = []
        for tag in soup.find_all(['p', 'h3', 'h4', 'span']):
            text = tag.get_text(strip=True).lower()
            if any(k in text for k in ['prof.', 'professor', 'instructor', 'faculty']):
                instructors.append(tag.get_text(strip=True))
            if len(instructors) >= 3:
                break

        # Extract weeks
        syllabus_text = soup.get_text()
        matches = re.findall(r'Week\s*(\d+).*?[:\s-]*(.+?)(?=\s*Week\s*\d+|\Z)', syllabus_text, re.I | re.DOTALL)

        weeks = {}
        for week_num_str, title in matches:
            week_num = int(week_num_str)
            clean_title = re.sub(r'^\s*[:\-\s]+', '', title.strip())
            clean_title = re.sub(r'\s+', ' ', clean_title)[:250]
            if clean_title and len(clean_title) > 3:
                weeks[week_num] = clean_title

        weeks = dict(sorted(weeks.items()))

        return {
            "title": course_title,
            "instructors": instructors[:3],
            "weeks": weeks,
            "url": url,
            "scraped_success": len(weeks) >= 4,
            "weeks_found": len(weeks)
        }

    except Exception as e:
        return {
            "title": "Failed to Load Course",
            "instructors": [],
            "weeks": {},
            "url": url,
            "scraped_success": False,
            "error": str(e)
        }