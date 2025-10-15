from selenium import webdriver
from selenium.webdriver.common.by import By
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
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


def save_results_pdf(data, output_file):
    """Save results to PDF file"""
    try:
        # Create PDF
        pdf = SimpleDocTemplate(output_file, pagesize=A4,
                               rightMargin=30, leftMargin=30,
                               topMargin=30, bottomMargin=18)
        
        # Container for PDF elements
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#000000'),
            alignment=TA_LEFT,
            fontName='Helvetica'
        )
        
        # Add title
        title = Paragraph("ECOURTS CAUSE LIST", title_style)
        elements.append(title)
        
        # Add generation date
        date_text = f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
        date_para = Paragraph(date_text, normal_style)
        elements.append(date_para)
        elements.append(Spacer(1, 0.3*inch))
        
        # Add summary
        summary = Paragraph(f"<b>Total Cases: {len(data)}</b>", heading_style)
        elements.append(summary)
        elements.append(Spacer(1, 0.2*inch))
        
        # Create table data
        table_data = [['S.No', 'Case Number', 'Parties', 'Purpose', 'Advocate']]
        
        for i, case in enumerate(data, 1):
            row = [
                str(case.get('serial_number', i)),
                Paragraph(case.get('case_number', 'N/A'), normal_style),
                Paragraph(case.get('parties', 'N/A')[:100], normal_style),
                Paragraph(case.get('purpose', 'N/A')[:50], normal_style),
                Paragraph(case.get('advocate', 'N/A')[:50], normal_style)
            ]
            table_data.append(row)
        
        # Create table
        table = Table(table_data, colWidths=[0.6*inch, 1.5*inch, 2.5*inch, 1.3*inch, 1.3*inch])
        
        # Style the table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
        
        # Build PDF
        pdf.build(elements)
        print(f"✓ Saved to: {output_file}")
        return True
    except Exception as e:
        print(f"❌ Error saving PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*60)
    print("ECOURTS SCRAPER - SEMI-AUTOMATIC MODE (PDF)")
    print("="*60)
    print("\nHow it works:")
    print("1. Browser opens automatically")
    print("2. YOU manually fill all fields on the website")
    print("3. Wait for results to appear")
    print("4. Press Enter here")
    print("5. Script extracts and saves data to PDF automatically")
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
            
            output_file = input("\n\nEnter filename (default: causelist.pdf): ").strip()
            if not output_file:
                output_file = "causelist.pdf"
            elif not output_file.endswith('.pdf'):
                output_file += '.pdf'
            
            save_results_pdf(results, output_file)
            
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
