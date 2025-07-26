import json
import time
import argparse
import os
from typing import List, Dict, Any
from playwright.sync_api import sync_playwright


class OpenRouterScraper:
    def __init__(self, include_free: bool = False):
        self.url = "https://openrouter.ai/models"
        self.search_terms = self._load_search_terms()
        self.current_search_term: str = ""
        self.include_free = include_free
    
    def _load_search_terms(self) -> List[str]:
        """Load search terms from model_strings.txt file"""
        # Try to find model_strings.txt in current directory or parent directories
        search_paths = [
            "model_strings.txt",  # Current directory
            "../../model_strings.txt",  # From src/opencosts to root
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "model_strings.txt")  # Absolute path to root
        ]
        
        for path in search_paths:
            try:
                with open(path, "r") as f:
                    terms = [line.strip() for line in f if line.strip()]
                    return terms
            except FileNotFoundError:
                continue
        
        print("Warning: model_strings.txt not found, using default search terms")
        return ["Gemini 2.5", "Sonnet 4", "Opus 4", "Kimi K2", "Deepseek R1"]
    
    def _clean_model_name(self, name: str) -> str:
        """Clean up model name by removing token counts and extra info"""
        # Remove token counts
        if 'tokens' in name.lower():
            name = name.split('tokens')[0].strip()
        
        # Remove trailing size indicators like "70B", "8B", etc.
        if name.endswith('B') or name.endswith('M'):
            parts = name.split()
            if len(parts) > 1 and (parts[-1].endswith('B') or parts[-1].endswith('M')):
                # Check if the last part is just a size indicator
                try:
                    float(parts[-1][:-1])  # Try to parse as number
                    name = ' '.join(parts[:-1])
                except ValueError:
                    pass  # Keep the name as is if it's not a number
        
        # Remove "Free variant" text
        if 'free variant' in name.lower():
            name = name.replace('Free variant', '').strip()
        
        # Remove "Self-Moderated variant" text
        if 'self-moderated variant' in name.lower():
            name = name.replace('Self-Moderated variant', '').strip()
        
        return name.strip()

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

            # Get all visible model cards after filtering - try multiple approaches
            model_names = []
            seen_models = set()  # Track duplicates across all approaches
            
            # Approach 1: Look for role="link" elements with colons
            try:
                page.wait_for_timeout(2000)
                model_cards = page.locator('[role="link"]').filter(has_text=':')
                count = model_cards.count()
                
                for i in range(count):
                    try:
                        model_card = model_cards.nth(i)
                        model_text = model_card.text_content()
                        if model_text:
                            lines = model_text.strip().split('\n')
                            clean_name = lines[0].strip() if lines else model_text.strip()
                            
                            # Clean up the name - remove token counts and extra info
                            clean_name = self._clean_model_name(clean_name)
                            
                            if ':' in clean_name and len(clean_name) < 150 and clean_name not in seen_models:
                                # Additional filtering to avoid page elements
                                if not clean_name.lower().startswith('models:') and clean_name.strip():
                                    seen_models.add(clean_name)
                                    model_names.append(clean_name)
                    except:
                        pass
            except:
                pass
            
            # Approach 2: Look for all links with colons (broader search)
            try:
                all_links = page.locator('a').all()
                
                for link in all_links:
                    try:
                        text = link.text_content()
                        if text and ':' in text and len(text) < 150:
                            lines = text.strip().split('\n')
                            first_line = lines[0].strip()
                            
                            # Clean up the name - remove token counts and extra info
                            first_line = self._clean_model_name(first_line)
                            
                            if ':' in first_line and len(first_line) < 100 and first_line not in seen_models:
                                if not first_line.lower().startswith('models:') and first_line.strip():
                                    seen_models.add(first_line)
                                    model_names.append(first_line)
                    except:
                        continue
            except:
                pass
            
            # Approach 3: Look for any element containing model-like text
            try:
                # Look for elements that might contain model names
                all_elements = page.locator('*').filter(has_text=':').all()
                
                for element in all_elements:
                    try:
                        text = element.text_content()
                        if text and ':' in text and len(text) < 150:
                            lines = text.strip().split('\n')
                            first_line = lines[0].strip()
                            if ':' in first_line and len(first_line) < 100 and first_line not in seen_models:
                                # Additional check to ensure it looks like a model name
                                if any(provider in first_line.lower() for provider in ['google', 'anthropic', 'deepseek', 'moonshot', 'tng', 'openai', 'meta']):
                                    seen_models.add(first_line)
                                    model_names.append(first_line)
                    except:
                        continue
            except:
                pass

            browser.close()
            
            # Final cleanup and deduplication
            cleaned_models = []
            final_seen = set()
            
            for model in model_names:
                cleaned = self._clean_model_name(model)
                if cleaned and ':' in cleaned and cleaned not in final_seen:
                    if not cleaned.lower().startswith('models:'):
                        # Filter out "(free)" models unless include_free is True
                        if not self.include_free and "(free)" in cleaned.lower():
                            continue
                        final_seen.add(cleaned)
                        cleaned_models.append(cleaned)
            
            return cleaned_models

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
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Scrape OpenRouter models")
    parser.add_argument("--include-free", action="store_true", 
                       help="Include models marked as '(free)' in the results")
    args = parser.parse_args()
    
    # Create scraper with the include_free option
    scraper = OpenRouterScraper(include_free=args.include_free)
    all_results = {}
    
    print(f"Scraping models with include_free={args.include_free}")
    if not args.include_free:
        print("Note: Models containing '(free)' will be filtered out. Use --include-free to include them.")
    
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
        "total_models_found": sum(len(models) for models in all_results.values()),
        "include_free": args.include_free
    }
    
    with open("all_models_combined.json", "w") as f:
        json.dump(combined_results, f, indent=2)
    
    print(f"\n{'='*50}")
    print("FINAL SUMMARY")
    print(f"{'='*50}")
    print(f"Total searches performed: {len(scraper.search_terms)}")
    print(f"Total models found across all searches: {sum(len(models) for models in all_results.values())}")
    print(f"Include free models: {args.include_free}")
    for search_term, models in all_results.items():
        print(f"  {search_term}: {len(models)} models")
