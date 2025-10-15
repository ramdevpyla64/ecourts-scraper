from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import time
from datetime import datetime
import sys

class ECourtsScraper:
    def __init__(self):
        """Initialize browser"""
        print("Initializing browser...")
        
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--log-level=3')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.maximize_window()
            print("✓ Browser started")
        except Exception as e:
            print(f"❌ Could not start browser: {e}")
            print("\nMake sure Chrome and ChromeDriver are installed")
            sys.exit(1)
        
        self.base_url = "https://services.ecourts.gov.in/ecourtindia_v6/"
    
    def navigate_to_cause_list(self):
        """Navigate to cause list page"""
        try:
            print("\nNavigating to eCourts website...")
            url = f"{self.base_url}?p=cause_list/index"
            self.driver.get(url)
            time.sleep(3)
            print("✓ Page loaded")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def extract_data(self):
        """Extract cause list data from current page"""
        try:
            print("\n[Extracting data from page...]")
            time.sleep(2)
            
            cause_list = []
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            
            for table in tables:
                try:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    if len(rows) < 2:
                        continue
                    
                    for row in rows[1:]:
                        cols = row.find_elements(By.TAG_NAME, "td")
                        if len(cols) >= 2:
                            case_info = {
                                'serial_number': cols[0].text.strip() if len(cols) > 0 else '',
                                'case_number': cols[1].text.strip() if len(cols) > 1 else '',
                                'parties': cols[2].text.strip() if len(cols) > 2 else '',
                                'purpose': cols[3].text.strip() if len(cols) > 3 else '',
                                'advocate': cols[4].text.strip() if len(cols) > 4 else '',
                            }
                            
                            if case_info['case_number'] or case_info['parties']:
                                cause_list.append(case_info)
                except:
                    continue
            
            if cause_list:
                print(f"✓ Extracted {len(cause_list)} cases")
            else:
                print("⚠ No cause list found")
                screenshot = f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.driver.save_screenshot(screenshot)
                print(f"Screenshot saved: {screenshot}")
            
            return cause_list
            
        except Exception as e:
            print(f"❌ Error extracting data: {e}")
            return []
    
    def close(self):
        """Close browser"""
        try:
            self.driver.quit()
            print("\n✓ Browser closed")
        except:
            pass


def save_results(data, output_file):
    """Save results to JSON and TXT files"""
    try:
        # Save JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved to: {output_file}")
        
        # Save TXT
        text_file = output_file.replace('.json', '.txt')
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("ECOURTS CAUSE LIST\n")
            f.write("="*80 + "\n\n")
            
            for i, case in enumerate(data, 1):
                f.write(f"\n{i}. Serial No: {case.get('serial_number', 'N/A')}\n")
                f.write(f"   Case Number: {case.get('case_number', 'N/A')}\n")
                f.write(f"   Parties: {case.get('parties', 'N/A')}\n")
                f.write(f"   Purpose: {case.get('purpose', 'N/A')}\n")
                f.write(f"   Advocate: {case.get('advocate', 'N/A')}\n")
                f.write("-"*80 + "\n")
        
        print(f"✓ Saved to: {text_file}")
        return True
    except Exception as e:
        print(f"❌ Error saving: {e}")
        return False
def main():
    print("="*60)
    print("ECOURTS SCRAPER - SEMI-AUTOMATIC MODE")
    print("="*60)
    print("\nHow it works:")
    print("1. Browser opens automatically")
    print("2. YOU manually fill all fields on the website")
    print("3. Wait for results to appear")
    print("4. Press Enter here")
    print("5. Script extracts and saves data automatically")
    print("="*60)  
    input("\nPress Enter to start...")
    scraper = None
    try:
        scraper = ECourtsScraper()
        if not scraper.navigate_to_cause_list():
            print("❌ Could not navigate. Opening base URL...")
            scraper.driver.get(scraper.base_url)
            time.sleep(3)
        print("\n📋 NOW DO THE FOLLOWING IN THE BROWSER:")
        print("="*60)
        print("1. Close any popup if it appears")
        print("2. Select State from dropdown")
        print("3. Select District")
        print("4. Select Court Complex")
        print("5. Select Court Name")
        print("6. Enter Date (DD-MM-YYYY)")
        print("7. Enter Captcha")
        print("8. Click 'Civil' or 'Criminal' button")
        print("9. Wait for cause list to appear")
        print("="*60)
        input("\n✅ Press Enter once you see the cause list on screen...")
        results = scraper.extract_data()
        
        if results:
            print(f"\n{'='*60}")
            print(f"SUCCESS - FOUND {len(results)} CASES")
            print(f"{'='*60}")
            print("\nSample Cases:")
            for i, case in enumerate(results[:5], 1):
                print(f"\n{i}. Serial No: {case.get('serial_number', 'N/A')}")
                print(f"   Case Number: {case.get('case_number', 'N/A')}")
                print(f"   Parties: {case.get('parties', 'N/A')[:60]}...")
                print(f"   Purpose: {case.get('purpose', 'N/A')}")
            
            if len(results) > 5:
                print(f"\n... and {len(results) - 5} more cases")
            output_file = input("\n\nEnter filename (default: causelist.json): ").strip()
            if not output_file:
                output_file = "causelist.json"
            save_results(results, output_file)
            print(f"\n{'='*60}")
            print("✅ COMPLETED SUCCESSFULLY!")
            print(f"{'='*60}")
        else:
            print("\n❌ No results found")
            print("Make sure the cause list table is visible on the page")
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if scraper:
            scraper.close()
    print("\n✓ Done!")
if __name__ == "__main__":
    main()
