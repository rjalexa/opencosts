import json
import time
from typing import List, Dict, Any
from playwright.sync_api import sync_playwright


class OpenRouterScraper:
    def __init__(self):
        self.url = "https://openrouter.ai/models"
        self.search_term = "Gemini 2.5"

    def scrape(self) -> List[str]:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.url)

            # Wait for the page to load
            page.wait_for_load_state("domcontentloaded")
            
            # Handle cookie dialog if present
            try:
                accept_button = page.locator('button:has-text("Accept")')
                if accept_button.is_visible(timeout=5000):
                    accept_button.click()
                    page.wait_for_timeout(1000)
            except:
                pass
            
            # Wait for models to load
            page.wait_for_timeout(3000)
            
            # Use the search input as requested
            try:
                search_input = page.get_by_placeholder('Filter models')
                search_input.fill(self.search_term)
                
                # Wait for the filtered results to load
                page.wait_for_timeout(3000)
            except Exception as e:
                print(f"Error with search input: {e}")
                browser.close()
                return []

            # Get all model cards by their accessible names using the improved approach
            model_cards = page.get_by_role('link').filter(has_text=r'Google:|OpenAI:|Anthropic:|Meta:')

            # Iterate through them and collect model names
            model_names = []
            count = model_cards.count()
            
            print(f"Found {count} model cards matching the filter criteria")
            
            for i in range(count):
                try:
                    model_card = model_cards.nth(i)
                    model_name = model_card.text_content()
                    if model_name:
                        # Extract just the model title (first line, usually contains the provider and model name)
                        lines = model_name.strip().split('\n')
                        clean_name = lines[0].strip() if lines else model_name.strip()
                        model_names.append(clean_name)
                        print(f"Model {i + 1}: {clean_name}")
                except Exception as e:
                    print(f"Error extracting data from model card {i + 1}: {e}")
            
            # If no models found with provider filter, look for Google Gemini models directly
            if not model_names:
                try:
                    # Look for any element containing "Google: Gemini" pattern
                    google_gemini_elements = page.locator('text=/Google.*Gemini/i').all()
                    
                    for element in google_gemini_elements:
                        try:
                            text = element.text_content()
                            if text and self.search_term.lower() in text.lower():
                                lines = text.strip().split('\n')
                                clean_name = lines[0].strip() if lines else text.strip()
                                if clean_name and len(clean_name) < 100:
                                    model_names.append(clean_name)
                                    print(f"Model {len(model_names)}: {clean_name}")
                        except:
                            continue
                            
                except Exception as e:
                    print(f"Error in fallback search: {e}")

            browser.close()
            return model_names

    def save_results(self, results: List[str], filename: str = "models.json"):
        # Convert list of model names to a structured format for JSON
        structured_data = {
            "search_term": self.search_term,
            "model_count": len(results),
            "models": results
        }
        with open(filename, "w") as f:
            json.dump(structured_data, f, indent=2)


if __name__ == "__main__":
    scraper = OpenRouterScraper()
    model_names = scraper.scrape()
    scraper.save_results(model_names)
    print(f"\nSummary: Found {len(model_names)} models for search term '{scraper.search_term}'")
    print("Model names:")
    for i, name in enumerate(model_names, 1):
        print(f"  {i}. {name}")
