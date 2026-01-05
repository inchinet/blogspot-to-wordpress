# Blogspot to WordPress Publisher

A simple web application to migrate your Blogspot posts to WordPress, preserving all text, images, and videos.

## Features

- 🚀 **Easy Migration**: Copy Blogspot posts to WordPress with a single click
- 📸 **Media Preservation**: Automatically downloads and uploads all images and videos
- 📅 **Date Organization**: Stores media in WordPress standard directory structure (`/wp-content/uploads/yyyy/mm`)
- 🎨 **Modern UI**: Clean, liquid glass design interface
- ✅ **Real-time Feedback**: Shows publication status and progress

## Prerequisites

- Python 3.7 or higher
- A WordPress site with REST API enabled
- WordPress Application Password (for authentication)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/inchinet/blogspot-to-wordpress.git
   cd blogspot-to-wordpress
   ```

2. **Install dependencies**
   
   The project uses Python from your existing environment. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### WordPress Application Password

1. Log in to your WordPress admin panel
2. Go to **Users** → **Profile**
3. Scroll down to **Application Passwords**
4. Enter a name (e.g., "Blogspot Migrator") and click **Add New Application Password**
5. Copy the generated password (format: `xxxx xxxx xxxx xxxx xxxx xxxx`)

### WordPress REST API

Ensure your WordPress site has the REST API enabled. Most modern WordPress installations have this enabled by default.

## Usage

### Web Interface

1. **Start the application**
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **Fill in the form**:
   - **Blogspot URL**: The full URL of your Blogspot post (e.g., `https://your-blog.blogspot.com/2025/04/post-title.html`)
   - **WordPress Site URL**: Your WordPress site URL (e.g., `https://yoursite.com`)
   - **WordPress Username**: Your WordPress username
   - **WordPress Password**: The Application Password you generated

4. **Click "Publish to WordPress"** and wait for confirmation

### Command Line Interface

For batch processing or automation:

```bash
python cli.py
```

Follow the prompts to enter:
- Blogspot URL
- WordPress site URL
- WordPress username
- WordPress application password

## How It Works

1. **Fetches Content**: Scrapes the Blogspot post HTML
2. **Extracts Media**: Identifies all images and videos in the post
3. **Downloads Media**: Downloads media files to temporary storage
4. **Uploads to WordPress**: Uploads media to WordPress media library
5. **Updates URLs**: Replaces Blogspot URLs with WordPress media URLs
6. **Creates Post**: Publishes the post to WordPress with all content intact
7. **Organizes Files**: Stores media in `/wp-content/uploads/yyyy/mm` based on original post date

## Project Structure

```
blogspot-to-wordpress/
├── app.py              # Flask web application
├── cli.py              # Command-line interface
├── wp_utils.py         # WordPress API utilities
├── requirements.txt    # Python dependencies
├── static/
│   ├── style.css      # Application styles
│   └── script.js      # Frontend JavaScript
└── templates/
    └── index.html     # Web interface template
```

## Troubleshooting

### 404 Error When Publishing

If you encounter a 404 error, ensure:
- Your WordPress REST API is accessible
- The WordPress URL is correct (no trailing slash)
- Your application password is valid

### Media Not Uploading

Check that:
- Your WordPress media upload directory has write permissions
- The media files are accessible from the Blogspot URL
- Your WordPress site allows the file types being uploaded

### Authentication Failed

Verify:
- You're using an Application Password, not your regular WordPress password
- The username is correct
- The Application Password has no spaces when entered

## Requirements

- **Python Packages**:
  - Flask (web framework)
  - Requests (HTTP library)
  - BeautifulSoup4 (HTML parsing)
  - lxml (XML/HTML parser)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

## Acknowledgments

Built to help bloggers easily migrate their content from Blogspot to WordPress while preserving all media and formatting.

---

**Note**: This tool is designed for personal use to backup and migrate your own Blogspot content. Please respect copyright and terms of service when using this tool.
