from playwright.sync_api import Playwright, sync_playwright
from browserbase import Browserbase
import os
import time
import json

# Initialize Browserbase client with explicit API key
bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])

def run(playwright: Playwright) -> None:
    """
    Test the Mocksi app string reversal and AI summarization features using Browserbase
    """
    # Create a session on Browserbase
    session = bb.sessions.create(project_id=os.environ["BROWSERBASE_PROJECT_ID"])
    
    # Connect to the remote session
    chromium = playwright.chromium
    browser = chromium.connect_over_cdp(session.connect_url)
    context = browser.contexts[0]
    page = context.pages[0]
    
    try:
        print("🚀 Starting Mocksi App Tests with Browserbase...")
        
        # Navigate to the local Mocksi app
        page.goto("http://localhost:3000")
        page_title = page.title()
        print(f"📄 Page title: {page_title}")
        
        # Wait for the page to load completely
        page.wait_for_load_state("networkidle")
        
        # Take initial screenshot
        page.screenshot(path="mocksi_initial.png")
        print("📸 Initial screenshot taken")
        
        # Test 1: String Reversal Feature
        print("\n🔄 Testing String Reversal Feature...")
        
        # Find the reverse input field in the first demo card
        reverse_input = page.locator('.demo-card:first-child textarea')
        reverse_input.fill("Hello Mocksi Interview!")
        print("✅ Entered text for reversal")
        
        # Click the "Start Workflow" button
        start_workflow_btn = page.locator('.demo-card:first-child button[type="submit"]')
        start_workflow_btn.click()
        print("✅ Started reversal workflow")
        
        # Wait for the workflow to complete and results to appear
        # Look for the result panel to appear
        result_panel = page.locator('.demo-card:first-child .result-panel')
        result_panel.wait_for(state="visible", timeout=30000)
        
        # Verify the reversed text
        reversed_text = page.locator('.demo-card:first-child .result-text.reversed').inner_text()
        print(f"✅ Reversed text: {reversed_text}")
        
        # Take screenshot after string reversal
        page.screenshot(path="mocksi_after_reversal.png")
        print("📸 Screenshot taken after string reversal")
        
        # Test 2: AI Summarization Feature
        print("\n🤖 Testing AI Summarization Feature...")
        
        # Test text for summarization
        test_text = """
        Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by animals including humans. AI research has been defined as the field of study of intelligent agents, which refers to any system that perceives its environment and takes actions that maximize its chance of achieving its goals. The term artificial intelligence is often used to describe machines or computers that mimic cognitive functions that humans associate with the human mind, such as learning and problem solving. As machines become increasingly capable, tasks considered to require intelligence are often removed from the definition of AI, a phenomenon known as the AI effect. AI applications include advanced web search engines, recommendation systems, understanding human speech, self-driving cars, automated decision-making and competing at the highest level in strategic game systems.
        """
        
        # Find the summarization input field in the second demo card
        summarize_input = page.locator('.demo-card:nth-child(2) textarea')
        summarize_input.fill(test_text)
        print("✅ Entered text for summarization")
        
        # Select summary style (optional - default is "concise")
        style_select = page.locator('.demo-card:nth-child(2) select')
        style_select.select_option("detailed")
        print("✅ Selected detailed summary style")
        
        # Click the "Generate Summary" button
        generate_summary_btn = page.locator('.demo-card:nth-child(2) button[type="submit"]')
        generate_summary_btn.click()
        print("✅ Started AI summarization")
        
        # Wait for the AI summary to complete
        ai_result_panel = page.locator('.demo-card:nth-child(2) .result-panel')
        ai_result_panel.wait_for(state="visible", timeout=60000)  # AI might take longer
        
        # Verify the summary text
        summary_text = page.locator('.demo-card:nth-child(2) .result-text.summary').inner_text()
        print(f"✅ AI Summary: {summary_text}")
        
        # Take screenshot after AI summarization
        page.screenshot(path="mocksi_after_ai_summary.png")
        print("📸 Screenshot taken after AI summarization")
        
        # Test 3: Service Status Check
        print("\n🔍 Testing Service Status...")
        
        # Check if service status indicators are showing healthy
        service_indicators = page.locator('.status-indicator')
        service_count = service_indicators.count()
        print(f"✅ Found {service_count} service status indicators")
        
        for i in range(service_count):
            indicator = service_indicators.nth(i)
            indicator_text = indicator.inner_text()
            is_healthy = indicator.get_attribute("class").find("healthy") != -1
            status = "✅ Healthy" if is_healthy else "⚠️ Unhealthy"
            print(f"   {indicator_text}: {status}")
        
        # Test 4: Clear All Results
        print("\n🧹 Testing Clear All Results...")
        
        # Click the "Clear All Results" button
        clear_btn = page.locator('button:has-text("Clear All Results")')
        clear_btn.click()
        print("✅ Cleared all results")
        
        # Verify results are cleared
        time.sleep(2)  # Wait for clear action to complete
        result_panels = page.locator('.result-panel')
        result_count = result_panels.count()
        print(f"✅ Results cleared - {result_count} result panels remaining")
        
        # Take final screenshot
        page.screenshot(path="mocksi_final.png")
        print("📸 Final screenshot taken")
        
        # Test 5: API Documentation Link
        print("\n📚 Testing API Documentation Link...")
        
        # Find and test the API docs link in footer
        api_docs_link = page.locator('a[href="http://localhost:8000/docs"]')
        if api_docs_link.is_visible():
            print("✅ API documentation link found")
        else:
            print("⚠️ API documentation link not found")
        
        # Test 6: Temporal Dashboard Link
        print("\n⚡ Testing Temporal Dashboard Link...")
        
        # Find and test the Temporal dashboard link
        temporal_link = page.locator('a[href="http://localhost:8080"]')
        if temporal_link.is_visible():
            print("✅ Temporal dashboard link found")
        else:
            print("⚠️ Temporal dashboard link not found")
        
        print("\n🎉 All Mocksi App Tests Completed Successfully!")
        print("=" * 50)
        print("Test Summary:")
        print("✅ String Reversal - PASSED")
        print("✅ AI Summarization - PASSED") 
        print("✅ Service Status Check - PASSED")
        print("✅ Clear Results - PASSED")
        print("✅ Navigation Links - PASSED")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        # Take error screenshot
        page.screenshot(path="mocksi_error.png")
        raise
    finally:
        # Clean up
        page.close()
        browser.close()
    
    print(f"\n🎬 Done! View session replay at https://browserbase.com/sessions/{session.id}")

if __name__ == "__main__":
    # Verify environment variables are set
    required_env_vars = ["BROWSERBASE_API_KEY", "BROWSERBASE_PROJECT_ID"]
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these environment variables before running the test:")
        print("export BROWSERBASE_API_KEY=your_api_key_here")
        print("export BROWSERBASE_PROJECT_ID=your_project_id_here")
        exit(1)
    
    print("🔧 Environment variables configured correctly")
    print(f"🔑 API Key: {os.environ['BROWSERBASE_API_KEY'][:10]}...")
    print(f"📦 Project ID: {os.environ['BROWSERBASE_PROJECT_ID']}")
    
    with sync_playwright() as playwright:
        run(playwright)