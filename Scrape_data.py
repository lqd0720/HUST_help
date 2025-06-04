from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import json
import time
import re

def setup_driver(headless=True):
    """Setup Chrome driver with appropriate options"""
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def wait_for_page_load(driver, timeout=30):
    """Wait for page to fully load"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        return True
    except TimeoutException:
        return False

def parse_course_row(row_text):
    """Parse a course row text into structured data"""
    
    row_text = row_text.strip()
    if not row_text:
        return None
    
    # Extract course code (first word)
    code_match = re.match(r'^(\S+)', row_text)
    if not code_match:
        return None
    
    course_code = code_match.group(1)
    remaining_text = row_text[len(course_code):].strip()
    
    # Try Pattern 1: Look for duration with parentheses
    duration_pattern = r'\s+(\d+(?:\.\d+)?\(\d+(?:\.\d+)?-\d+(?:\.\d+)?-\d+(?:\.\d+)?-\d+(?:\.\d+)?\))\s+'
    duration_match = re.search(duration_pattern, remaining_text)
    
    if duration_match:
        # Pattern 1: Full format with duration details
        duration = duration_match.group(1)
        
        # Extract course name (everything before duration)
        course_name = remaining_text[:duration_match.start()].strip()
        
        # Extract numeric values after duration (credits, credit_hours, weight)
        after_duration = remaining_text[duration_match.end():].strip()
        
        # Use regex to extract the numeric values at the end
        numeric_pattern = r'(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)(?:\s|$)'
        numeric_match = re.search(numeric_pattern, after_duration)
        
        if not numeric_match:
            return None
        
        credits = numeric_match.group(1)
        credit_hours = numeric_match.group(2)
        weight = numeric_match.group(3)
        
        # Parse duration details: 3(3-2-0-6) -> theory=3, lab=2, etc.
        duration_details = duration.split('(')[1].rstrip(')')
        duration_parts = duration_details.split('-')
        
        theory_hours = duration_parts[0] if len(duration_parts) > 0 else ""
        lab_hours = duration_parts[1] if len(duration_parts) > 1 else ""
        practice_hours = duration_parts[2] if len(duration_parts) > 2 else ""
        self_study_hours = duration_parts[3] if len(duration_parts) > 3 else ""
        
    else:
        # Pattern 2: Simplified format without duration details
        # Extract numeric values at the end (last 3 numbers)
        numeric_pattern = r'(.+?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)(?:\s|$)'
        match = re.match(numeric_pattern, remaining_text)
        
        if not match:
            return None
        
        course_name = match.group(1).strip()
        credits = match.group(2)
        credit_hours = match.group(3)
        weight = match.group(4)
        
        # Set duration to credits value since no detailed breakdown available
        duration = credits
        theory_hours = credits
        lab_hours = ""
        practice_hours = ""
        self_study_hours = ""
    
    return {
        "Mã học phần": course_code,
        "Tên học phần": course_name,
        "Thời lượng": duration,
        "Tín chỉ": credits,
        "Tiết tín chỉ": credit_hours,
        "Trọng số": weight,
        "Tiết lý thuyết": theory_hours,
        "Tiết thí nghiệm": lab_hours,
        "Tiết bài tập": practice_hours,
        "Tiết tự học": self_study_hours
    }

def extract_courses_from_page(driver):
    """Extract course data from current page"""
    courses = []
    
    try:
        # Wait for the course list to load
        wait = WebDriverWait(driver, 10)
        
        # Look for the table containing course data
        # Try different selectors
        table_selectors = [
            "//table[contains(@class, 'GridView')]",
            "//table[contains(@id, 'GridView')]",
            "//table[contains(@id, 'gv')]",
            "//div[@class='content']//table",
            "//table"
        ]
        
        table = None
        for selector in table_selectors:
            try:
                tables = driver.find_elements(By.XPATH, selector)
                for t in tables:
                    rows = t.find_elements(By.TAG_NAME, "tr")
                    if len(rows) > 5:  # Likely the main data table
                        table = t
                        break
                if table:
                    break
            except:
                continue
        
        if not table:
            print("No suitable table found")
            return courses
        
        # Get all data rows (skip header)
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]
        print(f"Found {len(rows)} data rows")
        
        for i, row in enumerate(rows):
            try:
                # Get row text and try to parse it
                row_text = row.text.strip()
                if not row_text or len(row_text.split()) < 4:
                    continue
                
                print(f"Processing row {i+1}: {row_text[:50]}...")
                
                # Parse the course data from text
                course_data = parse_course_row(row_text)
                if not course_data:
                    print(f"  Could not parse row: {row_text}")
                    continue
                
                courses.append(course_data)
                print(f"  ✓ Added: {course_data['Mã học phần']} - {course_data['Tên học phần']}")
                
            except Exception as e:
                print(f"Error processing row {i}: {e}")
                continue
    
    except Exception as e:
        print(f"Error extracting courses: {e}")
    
    return courses

def navigate_pages(driver, max_pages=3):
    """Navigate through multiple pages and collect all courses"""
    all_courses = []
    current_page = 1
    
    while current_page <= max_pages:
        print(f"\n=== Processing Page {current_page} ===")
        
        # Extract courses from current page
        courses = extract_courses_from_page(driver)
        all_courses.extend(courses)
        
        print(f"Collected {len(courses)} courses from page {current_page}")
        print(f"Total courses so far: {len(all_courses)}")
        
        # Try to go to next page
        try:
            # Look for next page link
            next_links = driver.find_elements(By.XPATH, f"//a[text()='{current_page + 1}']")
            if not next_links:
                # Try alternative selectors for pagination
                next_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'Page$')]")
                next_links = [link for link in next_links if link.text == str(current_page + 1)]
            
            if next_links:
                print(f"Navigating to page {current_page + 1}...")
                ActionChains(driver).move_to_element(next_links[0]).click().perform()
                time.sleep(3)  # Wait for page to load
                current_page += 1
            else:
                print("No more pages found")
                break
                
        except Exception as e:
            print(f"Error navigating to next page: {e}")
            break
    
    return all_courses

def main():
    driver = setup_driver(headless=False)  # Set to True for production
    
    try:
        print("Navigating to HUST course list...")
        driver.get("http://sis.hust.edu.vn/ModuleProgram/CourseLists.aspx")
        
        # Wait for page to load
        if not wait_for_page_load(driver):
            print("Page load failed")
            return
        
        time.sleep(5)  # Additional wait for dynamic content
        
        print(f"Page loaded. Title: {driver.title}")

        all_courses = navigate_pages(driver, max_pages=408)
        
        print(f"\n=== SCRAPING COMPLETE ===")
        print(f"Total courses collected: {len(all_courses)}")
        
        if all_courses:
            # Save to JSON
            with open("hust_courses.json", "w", encoding="utf-8") as f:
                json.dump(all_courses, f, ensure_ascii=False, indent=2)
            
            print("Data saved to hust_courses.json")
            
            # Show sample data
            print("\nSample courses:")
            for course in all_courses[:5]:
                print(f"  {course['Mã học phần']}: {course['Tên học phần']} ({course['Tín chỉ']} credits)")
        else:
            print("No courses were collected")
    
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    finally:
        input("Press Enter to close browser...")
        driver.quit()

if __name__ == "__main__":
    main()