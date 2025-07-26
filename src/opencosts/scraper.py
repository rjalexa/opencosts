import json
import time
from typing import List, Dict, Any
from playwright.sync_api import sync_playwright


class OpenRouterScraper:
    def __init__(self):
        self.url = "https://openrouter.ai/models"
        self.search_terms = ["Gemini 2.5", "Sonnet 4", "Opus 4", "Kimi K2", "Deepseek R1"]
        self.current_search_term: str = ""

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
                search_input.fill(self.current_search_term)
                
                # Wait for the filtered results to load
                page.wait_for_timeout(3000)
            except Exception as e:
                print(f"Error with search input: {e}")
                browser.close()
                return []

            # Get all visible model cards after filtering
            try:
                # Wait a bit more for the filter to take effect
                page.wait_for_timeout(2000)
                
                # Look for model cards using a more generic approach
                # Try different selectors to find the model cards
                model_cards = page.locator('[role="link"]').filter(has_text=':')
                count = model_cards.count()
                
                model_names = []
                for i in range(count):
                    try:
                        model_card = model_cards.nth(i)
                        model_text = model_card.text_content()
                        if model_text:
                            # Extract the first line which usually contains the provider and model name
                            lines = model_text.strip().split('\n')
                            clean_name = lines[0].strip() if lines else model_text.strip()
                            
                            # Only include if it contains a colon (provider: model format) and is reasonable length
                            if ':' in clean_name and len(clean_name) < 150:
                                model_names.append(clean_name)
                    except Exception as e:
                        pass  # Silently handle errors
                        
            except Exception as e:
                print(f"Error finding model cards: {e}")
                model_names = []
            
            # If still no results, try a broader search
            if not model_names:
                try:
                    # Look for any text elements that might contain model information
                    all_links = page.locator('a').all()
                    
                    for link in all_links:
                        try:
                            text = link.text_content()
                            if text and ':' in text and len(text) < 150:
                                # Check if this looks like a model name
                                lines = text.strip().split('\n')
                                first_line = lines[0].strip()
                                if ':' in first_line and len(first_line) < 100:
                                    model_names.append(first_line)
                                    
                                    # Limit to prevent too many results
                                    if len(model_names) >= 50:
                                        break
                        except:
                            continue
                            
                except Exception as e:
                    pass  # Silently handle errors

            browser.close()
            return model_names

    def save_results(self, results: List[str], filename: str = "models.json"):
        # Convert list of model names to a structured format for JSON
        structured_data = {
            "search_term": self.current_search_term,
            "model_count": len(results),
            "models": results
        }
        with open(filename, "w") as f:
            json.dump(structured_data, f, indent=2)


if __name__ == "__main__":
    scraper = OpenRouterScraper()
    all_results = {}
    
    for search_term in scraper.search_terms:
        print(f"Searching for: {search_term}...")
        
        scraper.current_search_term = search_term
        model_names = scraper.scrape()
        
        # Save results for each search term with a unique filename
        filename = f"models_{search_term.replace(' ', '_').replace('.', '_').lower()}.json"
        scraper.save_results(model_names, filename)
        
        # Store results for summary
        all_results[search_term] = model_names
        
        print(f"Found {len(model_names)} models for '{search_term}'")
        for i, name in enumerate(model_names, 1):
            print(f"  {i}. {name}")
    
    # Save combined results
    combined_results = {
        "search_summary": {
            search_term: {
                "model_count": len(models),
                "models": models
            }
            for search_term, models in all_results.items()
        },
        "total_searches": len(scraper.search_terms),
        "total_models_found": sum(len(models) for models in all_results.values())
    }
    
    with open("all_models_combined.json", "w") as f:
        json.dump(combined_results, f, indent=2)
    
    print(f"\n{'='*50}")
    print("FINAL SUMMARY")
    print(f"{'='*50}")
    print(f"Total searches performed: {len(scraper.search_terms)}")
    print(f"Total models found across all searches: {sum(len(models) for models in all_results.values())}")
    for search_term, models in all_results.items():
        print(f"  {search_term}: {len(models)} models")
