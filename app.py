import logging
from flask import Flask, render_template, request, jsonify
import wp_utils as utils
import importlib
importlib.reload(utils)  # Refresh module
import traceback
import os
import inspect
import time
import sys

# VERSION v11
VERSION = "v11 (OMEGA_MARKER)"

# DEBUG: Verify loaded utils module
print(f"DEBUG: app.py loaded - {VERSION}")
print(f"DEBUG: sys.path: {sys.path[:3]}") # Check if . is first
print(f"DEBUG: wp_utils file: {utils.__file__}")
try:
    print(f"DEBUG: wp_utils VERSION: {getattr(utils, 'VERSION', 'UNKNOWN')}")
    source = inspect.getsource(utils.final_publish_v11)
    print(f"DEBUG: final_publish_v11 OMEGA_FUNC_PUBLISH found: {'OMEGA_MARKER_FUNC_PUBLISH' in source}")
    source_endpoint = inspect.getsource(utils.get_api_endpoint)
    print(f"DEBUG: get_api_endpoint OMEGA_FUNC_ENDPOINT found: {'OMEGA_MARKER_FUNC_ENDPOINT' in source_endpoint}")
except Exception as e:
    print(f"DEBUG: Could not get source: {e}")

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'
)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/publish', methods=['POST'])
def publish():
    try:
        data = request.json
        source_url = data.get('source_url')
        wp_url = data.get('wp_url')
        username = data.get('username')
        password = data.get('password')

        if not all([source_url, wp_url, username, password]):
            return jsonify({'success': False, 'message': 'Missing required fields.'}), 400

        logging.info(f"Starting publish process for {source_url} (wp_utils VERSION: {getattr(utils, 'VERSION', 'UNKNOWN')})")

        # 1. Scrape
        try:
            logging.info("Step 1: Scraping Blogspot...")
            scraped_data = utils.scrape_blogspot(source_url)
            logging.info("Scraping successful.")
        except Exception as e:
            logging.error(f"Scraping failed: {e}")
            return jsonify({'success': False, 'message': f'Failed to scrape Blogspot: {str(e)}'}), 500

        # 2. Process Media & Upload
        try:
            logging.info("Step 2: Processing media...")
            final_content = utils.process_content_and_upload_media(
                scraped_data['content'], 
                wp_url, 
                username, 
                password,
                post_date=scraped_data.get('post_date')
            )
            logging.info("Media processing successful.")
            logging.info(f"Final content preview (first 500 chars): {final_content[:500]}")
        except Exception as e:
            logging.error(f"Media processing failed: {e}")
            return jsonify({'success': False, 'message': f'Failed to process media: {str(e)}'}), 500

        # 3. Publish
        try:
            logging.info("Step 3: Publishing to WordPress...")
            print("DEBUG: Calling final_publish_v11 now...")
            result = utils.final_publish_v11(
                scraped_data['title'],
                final_content,
                wp_url,
                username,
                password,
                post_date=scraped_data.get('post_date')
            )
            logging.info(f"Published successfully: {result.get('link')}")
        except Exception as e:
            logging.error(f"Publishing failed: {e}")
            return jsonify({'success': False, 'message': f'Failed to publish to WordPress: {str(e)}'}), 500

        return jsonify({'success': True, 'message': 'Passage is published', 'link': result.get('link')})

    except Exception as e:
        logging.critical(f"Unhandled exception: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print(f"--- FRESH START: {VERSION} ---")
    print("--- If you don't see this message, RESTART process ---")
    print("="*50 + "\n")
    print("Starting Flask server on port 5000...")
    print("Open http://127.0.0.1:5000 in your browser.")
    # Debug is False for stability. Reloader disabled to prevent double execution.
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=5000)
