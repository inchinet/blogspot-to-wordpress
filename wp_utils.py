import requests
from bs4 import BeautifulSoup
import os
import base64
import re
from urllib.parse import urljoin, urlparse
import logging

# VERSION v12.2.0 - URL_REPLACE_DEBUG
VERSION = "v12.2.0"
print(f"!!! CRITICAL: wp_utils.py LOADED - VERSION {VERSION} !!!")
TIMEOUT = 30

def get_auth_header(username, password):
    credentials = f"{username}:{password}"
    token = base64.b64encode(credentials.encode()).decode('utf-8')
    return {'Authorization': f'Basic {token}'}

def clean_wp_url(url):
    """
    Cleans the WordPress URL to get the base URL.
    Removes trailing slashes, 'wp-json', 'index.php', and query parameters.
    """
    if not url:
        return ""
    url = url.strip()
    
    # Remove common API paths and suffixes
    for suffix in ['/wp-json/wp/v2/posts', '/wp-json/wp/v2/media', '/wp-json', '/index.php']:
        if suffix in url:
            url = url.split(suffix)[0]
        
    # Remove query parameters
    if '?' in url:
        url = url.split('?')[0]
    
    # Remove trailing slash(es)
    url = url.rstrip('/')
    return url

def get_api_endpoint(base_url, endpoint="/wp/v2/posts"):
    """
    Consistently constructs the API endpoint using the rest_route parameter.
    OMEGA_MARKER_FUNC_ENDPOINT
    """
    clean_base = clean_wp_url(base_url)
    res = f"{clean_base}/index.php?rest_route={endpoint}"
    print(f"DEBUG_GET_API_ENDPOINT: base='{base_url}' -> clean='{clean_base}' -> final='{res}'")
    return res

def scrape_blogspot(url):
    """
    Scrapes a Blogspot post for title and content.
    Returns:
    dict: {'title': str, 'content': soup_object, 'post_date': str}
    """
    try:
        logging.info(f"Fetching {url}")
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Selectors (common Blogspot themes)
        title_tag = soup.select_one('.post-title, .entry-title')
        content_tag = soup.select_one('.post-body, .entry-content')
        
        if not title_tag or not content_tag:
            raise ValueError("Could not find title or content in the Blogspot page.")

        title = title_tag.get_text(strip=True)
        logging.info(f"Found title: {title}")

        # Extract date from URL (e.g., .../2025/04/...)
        post_date = "2000-01-01T00:00:00" # Default fallback
        date_match = re.search(r'/(\d{4})/(\d{2})/', url)
        if date_match:
            year = date_match.group(1)
            month = date_match.group(2)
            post_date = f"{year}-{month}-01T12:00:00"
            logging.info(f"Extracted date from URL: {post_date}")

        # We perform operations on content_tag, so return the soup object/tag copy to avoid issues
        return {'title': title, 'content': content_tag, 'post_date': post_date} 
    except Exception as e:
        logging.error(f"Error scraping {url}: {e}")
        raise Exception(f"Scraping error: {str(e)}")

def upload_media(media_url, wp_url, username, password, date=None):
    """
    Downloads media from media_url and uploads it to WordPress.
    Returns the new WordPress media source URL and ID.
    'date' should be in ISO format: YYYY-MM-DDTHH:MM:SS
    """
    try:
        logging.info(f"Downloading media: {media_url}")
        # Download media
        media_resp = requests.get(media_url, stream=True, timeout=120) # Longer timeout for media
        media_resp.raise_for_status()
        
        filename = os.path.basename(urlparse(media_url).path)
        if not filename or filename == '':
            filename = 'media_item.jpg' # Default backup
        
        # Helper to get MIME type (simple guess)
        content_type = media_resp.headers.get('content-type')
        
        headers = get_auth_header(username, password)
        headers['Content-Disposition'] = f'attachment; filename={filename}'
        if content_type:
            headers['Content-Type'] = content_type

        # Ensure we have clean base URL and construct media API endpoint
        # OMEGA_MARKER_FUNC_UPLOAD
        api_url = get_api_endpoint(wp_url, "/wp/v2/media")
        
        # If date is provided, add it as a query parameter
        if date:
            api_url += f"&date={date}"
        
        logging.info(f"Uploading to {api_url}")

        logging.info(f"DEBUG: Uploading media to: {api_url}")
        upload_resp = requests.post(
            api_url, 
            headers=headers, 
            data=media_resp.content, # Use content instead of raw to avoid [WinError 6]
            timeout=300 # 5 minutes timeout for large files
        )
        
        logging.info(f"Upload response status: {upload_resp.status_code}")
        upload_resp.raise_for_status()
        
        data_json = upload_resp.json()
        logging.info(f"Upload successful! ID: {data_json.get('id')}, URL: {data_json.get('source_url')}")
        return data_json['source_url'], data_json['id']
    
    except Exception as e:
        logging.error(f"Failed to upload {media_url}: {e}")
        logging.error(f"Exception type: {type(e).__name__}")
        if hasattr(e, 'response'):
            logging.error(f"Response status: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")
            logging.error(f"Response text: {e.response.text[:200] if hasattr(e.response, 'text') else 'N/A'}")
        # We return None so the caller can decide to keep original URL or strip it
        return None, None

def process_content_and_upload_media(soup_content, wp_url, username, password, post_date=None):
    """
    Finds images and videos in the soup_content, uploads them to WP,
    and replaces the src URLs.
    """
    try:
        # Track URL mappings: old_url -> new_url
        url_mapping = {}
        
        # 1. Process Images
        images = soup_content.find_all('img')
        logging.info(f"Found {len(images)} images to process.")
        
        for img in images:
            src = img.get('src')
            if src:
                # Handle relative URLs if any (Blogspot usually absolute)
                if not src.startswith('http'):
                   continue 

                new_src, media_id = upload_media(src, wp_url, username, password, date=post_date)
                if new_src:
                    logging.info(f"Replacing image URL: {src[:80]}... -> {new_src}")
                    img['src'] = new_src
                    # Track the mapping
                    url_mapping[src] = new_src
                    # Clean up other attributes
                    if img.get('srcset'): del img['srcset']
                    if img.get('width'): del img['width']
                    if img.get('height'): del img['height']
                else:
                    logging.warning(f"Could not upload image {src[:80]}..., keeping original.")

        # 2. Process Videos
        videos = soup_content.find_all('video')
        logging.info(f"Found {len(videos)} videos to process.")
        
        for video in videos:
            src = video.get('src')
            if not src:
                # Check source tags
                source = video.find('source')
                if source:
                    src = source.get('src')
            
            if src:
                new_src, media_id = upload_media(src, wp_url, username, password, date=post_date)
                if new_src:
                    video['src'] = new_src
                    url_mapping[src] = new_src
                    if video.find('source'):
                        video.find('source')['src'] = new_src
        
        # 3. Process Anchor Tags - Replace href attributes that point to Blogspot media
        anchors = soup_content.find_all('a')
        logging.info(f"Found {len(anchors)} anchor tags to check.")
        replaced_anchors = 0
        
        for anchor in anchors:
            href = anchor.get('href')
            if href:
                # Check if this href matches any of the original media URLs we uploaded
                # We need to check against all keys in url_mapping
                for old_url, new_url in url_mapping.items():
                    # Check if the href contains the old URL or is a variant of it
                    # Blogspot often has different sizes in URLs (e.g., /s1345/ vs /s1600/)
                    if 'blogger.googleusercontent.com' in href or 'blogspot.com' in href:
                        # Extract the filename from both URLs to match them
                        old_filename = old_url.split('/')[-1].split('.')[0]  # Get base filename without extension
                        href_filename = href.split('/')[-1].split('.')[0]
                        
                        if old_filename and href_filename and old_filename in href_filename:
                            logging.info(f"Replacing anchor href: {href[:80]}... -> {new_url}")
                            anchor['href'] = new_url
                            replaced_anchors += 1
                            break
        
        logging.info(f"Replaced {replaced_anchors} anchor tag hrefs.")
        
        return str(soup_content)
    except Exception as e:
         logging.error(f"Error in processing content: {e}")
         raise e

def final_publish_v11(title, content_html, wp_url, username, password, post_date=None):
    """
    Publishes the post to WordPress.
    OMEGA_MARKER_FUNC_PUBLISH
    """
    try:
        headers = get_auth_header(username, password)
        headers['Content-Type'] = 'application/json'
        
        # Construct post API endpoint
        api_url = get_api_endpoint(wp_url, "/wp/v2/posts")
        
        print(f"DEBUG_RUNTIME_PUBLISH: wp_url='{wp_url}'")
        print(f"DEBUG_RUNTIME_PUBLISH: api_url='{api_url}'")
        logging.info(f"DEBUG_RUNTIME_PUBLISH: api_url='{api_url}'")
        
        payload = {
            'title': title,
            'content': content_html,
            'status': 'publish' 
        }

        if post_date:
            payload['date'] = post_date
        
        logging.info(f"Publishing post '{title}' to {api_url}")
        
        # Set allow_redirects=False and manually check for redirects to debug 404 issues
        response = requests.post(api_url, headers=headers, json=payload, timeout=TIMEOUT, allow_redirects=False)
        
        if response.status_code in [301, 302, 307, 308]:
             redirect_url = response.headers.get('Location')
             logging.warning(f"Redirect detected to: {redirect_url}")
             raise Exception(f"Server tried to redirect to {redirect_url}. This usually breaks the API.")
             
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        logging.error(f"Publishing error: {e}")
        if isinstance(e, requests.exceptions.HTTPError):
             logging.error(f"HTTP Error Details: {e.response.text[:200]}")
        
        raise Exception(f"Publishing failed: {str(e)}")
