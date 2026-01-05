from utils import scrape_blogspot, process_content_and_upload_media, publish_post
import traceback
import getpass

def main():
    print("=========================================")
    print("   Blogspot to WordPress CLI Publisher   ")
    print("=========================================")
    print("NOTE: This program will NOT shutdown your PC.")
    print("It simply uploads content to your WordPress site.")
    print("=========================================")

    try:
        source_url = input("Enter Blogspot Source URL: ").strip()
        if not source_url:
            print("Error: Source URL is required.")
            return

        wp_url = input("Enter WordPress Site URL [default: https://cwchin.no-ip.com/]: ").strip()
        if not wp_url:
            wp_url = "https://cwchin.no-ip.com/"

        username = input("Enter WP Username [default: inchinetwp]: ").strip()
        if not username:
            username = "inchinetwp"

        # Ask for password securely or allow pasting
        print(f"Enter WP App Password for user '{username}' (input will be hidden):")
        password = getpass.getpass("Password: ").strip()
        if not password:
             # Fallback for easier testing if getpass is annoying in some terminals, 
             # though getpass is standard. Let's allowing typing if empty? 
             # No, empty password is bad.
             print("Password is empty. Trying to read plain text input just in case...")
             password = input("Password (visible): ").strip()

        print("\n--- Starting Process ---")
        
        # 1. Scrape
        print(f"1. Scraping {source_url}...")
        scraped_data = scrape_blogspot(source_url)
        print("   -> Scrape successful!")
        print(f"   -> Title: {scraped_data['title']}")

        # 2. Process Media
        print("2. Processing content and uploading media...")
        final_content = process_content_and_upload_media(
            scraped_data['content'], 
            wp_url, 
            username, 
            password
        )
        print("   -> Media processing complete.")

        # 3. Publish
        print("3. Publishing to WordPress...")
        result = publish_post(
            scraped_data['title'],
            final_content,
            wp_url,
            username,
            password
        )
        print("=========================================")
        print("SUCCESS! Post published.")
        print(f"Link: {result.get('link')}")
        print("=========================================")
        
    except Exception as e:
        print("\nERROR OCCURRED:")
        traceback.print_exc()

    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
