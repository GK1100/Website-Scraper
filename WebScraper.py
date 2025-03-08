import requests
from bs4 import BeautifulSoup
import csv
import time
from urllib.parse import urljoin, urlparse
import asyncio
import aiohttp
from ollama import Client
import re
import gradio as gr
import pandas as pd

class OllamaWebScraper:
    def __init__(self, start_url, max_pages=100, output_file="OUTPUT.csv", model="llama3"):
        self.start_url = start_url
        self.base_domain = urlparse(start_url).netloc
        self.visited_urls = set()
        self.urls_to_visit = [start_url]
        self.max_pages = max_pages
        self.output_file = output_file
        self.ollama_client = Client()
        self.model = model
        
        # Initialize CSV file with headers
        with open(self.output_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['URL', 'Title', 'Summary', 'Content', 'Links'])
    
    async def fetch_url(self, session, url):
        try:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"Error fetching {url}: HTTP Status {response.status}")
                    return None
        except Exception as e:
            print(f"Exception fetching {url}: {str(e)}")
            return None
    
    def extract_links(self, soup, base_url):
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href and not href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                full_url = urljoin(base_url, href)
                if urlparse(full_url).netloc == self.base_domain:
                    links.append(full_url)
        return links
    
    def extract_content(self, soup):
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
        text = soup.get_text(separator=' ')
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        return text
    
    async def get_ollama_summary(self, content):
        if not content or len(content) < 50:
            return "No meaningful content to summarize"
        
        truncated_content = content[:4000]
        
        try:
            prompt = f"""Summarize the following webpage content in 2-3 sentences:

Content:
{truncated_content}

Summary:"""
            
            response = self.ollama_client.generate(
                model=self.model,
                prompt=prompt,
            )
            
            summary = response['response']
            summary = re.sub(r'\n+', ' ', summary).strip()
            return summary
            
        except Exception as e:
            print(f"Error generating summary with Ollama: {str(e)}")
            return "Failed to generate summary"
    
    async def crawl(self):
        async with aiohttp.ClientSession() as session:
            page_count = 0
            
            while self.urls_to_visit and page_count < self.max_pages:
                current_url = self.urls_to_visit.pop(0)
                
                if current_url in self.visited_urls:
                    continue
                
                print(f"Crawling: {current_url}")
                self.visited_urls.add(current_url)
                page_count += 1
                
                html_content = await self.fetch_url(session, current_url)
                
                if html_content:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    title = soup.title.string if soup.title else "No title"
                    content = self.extract_content(soup)
                    summary = await self.get_ollama_summary(content)
                    links = self.extract_links(soup, current_url)
                    self.save_to_csv(current_url, title, summary, content, links)
                    for link in links:
                        if link not in self.visited_urls and link not in self.urls_to_visit:
                            self.urls_to_visit.append(link)
                
                await asyncio.sleep(1)
        
        print(f"Crawling completed. Visited {len(self.visited_urls)} pages.")
        print(f"Results saved to {self.output_file}")
        return self.output_file
    
    def save_to_csv(self, url, title, summary, content, links):
        try:
            with open(self.output_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                links_str = ', '.join(links[:10])
                if len(links) > 10:
                    links_str += f" and {len(links) - 10} more"
                writer.writerow([url, title, summary, content, links_str])
        except Exception as e:
            print(f"Error saving to CSV: {str(e)}")

# Gradio function to run the crawler and display results
def run_scraper(start_url, max_pages, output_file, model):
    scraper = OllamaWebScraper(start_url, max_pages, output_file, model)
    asyncio.run(scraper.crawl())
    
    # Read the CSV file and return it as a DataFrame for display
    try:
        df = pd.read_csv(output_file)
        return f"Crawling completed. Results saved to {output_file}.", df
    except Exception as e:
        return f"Error reading CSV: {str(e)}", None

# Gradio UI
with gr.Blocks(title="Ollama Web Scraper") as demo:
    gr.Markdown("# Ollama Web Scraper")
    gr.Markdown("Enter the details below to crawl a website and generate summaries using Ollama.")
    
    with gr.Row():
        with gr.Column():
            start_url_input = gr.Textbox(label="Start URL", value="https://www.dsu.edu.in/")
            max_pages_input = gr.Slider(label="Max Pages to Crawl", minimum=1, maximum=500, value=100, step=1)
            output_file_input = gr.Textbox(label="Output CSV File", value="dsu_website_content.csv")
            model_input = gr.Dropdown(
                label="Ollama Model",
                choices=["llama3", "llama3.2:1b", "mistral", "gemma"],
                value="llama3.2:1b"
            )
            submit_btn = gr.Button("Start Crawling")
        
        with gr.Column():
            output_status = gr.Textbox(label="Status", interactive=False)
            output_table = gr.Dataframe(label="Results", interactive=False)
    
    # Connect the button to the scraper function
    submit_btn.click(
        fn=run_scraper,
        inputs=[start_url_input, max_pages_input, output_file_input, model_input],
        outputs=[output_status, output_table]
    )

# Launch the Gradio app
demo.launch()