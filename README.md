# Website-Scraper
A web scraping tool that crawls websites and generates AI-powered summaries using Ollama models, with a user-friendly Gradio interface.

## What This Tool Does

This application:
- Crawls websites within a specific domain
- Extracts content from each web page
- Uses Ollama AI models to generate summaries
- Saves all data to CSV files
- Provides a simple interface to control the process

## Step-by-Step Installation Guide

### Step 1: Set Up Prerequisites

1. Make sure you have Python 3.7 or newer installed
   ```bash
   python --version
   ```

2. Install Ollama by following these steps:
   - Go to https://github.com/ollama/ollama
   - Follow the installation instructions for your operating system
   - Start the Ollama server

3. Pull at least one Ollama model:
   ```bash
   ollama pull llama3.2:1b
   ```

### Step 2: Get the Code

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/ollama-web-scraper.git
   ```

2. Navigate to the project folder:
   ```bash
   cd ollama-web-scraper
   ```

### Step 3: Install Required Packages

Install all needed Python packages:
```bash
pip install requests beautifulsoup4 aiohttp ollama gradio pandas
```

## Step-by-Step Usage Guide

### Step 1: Start the Application

Run the application:
```bash
python app.py
```

This will open a web interface at `http://localhost:7860` in your browser.

### Step 2: Configure the Crawler

In the Gradio interface:
1. Enter the website URL you want to crawl in the "Start URL" field
   - Example: `https://www.dsu.edu.in/`

2. Set how many pages to crawl using the "Max Pages" slider
   - Start with a small number (10-20) for testing

3. Enter a filename for the output CSV
   - Example: `website_data.csv`

4. Select an Ollama model from the dropdown
   - Recommended: `llama3.2:1b` (faster) or `llama3` (higher quality)

### Step 3: Run the Crawler

1. Click the "Start Crawling" button

2. Watch the status updates in the interface
   - The crawler will visit pages one by one
   - The status will show the progress

### Step 4: View and Use Results

1. When crawling completes, you'll see:
   - A success message
   - A table showing the crawled data

2. Find your CSV file in the project directory:
   - It contains columns for URL, Title, Summary, Content, and Links
   - Open it with Excel or any spreadsheet program

3. Analyze the data:
   - Read the AI-generated summaries
   - Review the content extracted from each page
   - See which pages link to each other

## Understanding How It Works

The process follows these steps:

1. **Initialization**:
   - Sets up the starting URL and domain
   - Prepares the CSV file with headers

2. **Crawling Loop**:
   - Visits each URL one at a time
   - Keeps track of visited pages
   - Respects the max page limit

3. **For Each Page**:
   - Downloads the HTML content
   - Extracts the title and main text
   - Finds all links to other pages on the same domain

4. **AI Processing**:
   - Sends the page content to Ollama
   - Gets back a 2-3 sentence summary

5. **Data Storage**:
   - Saves all information to the CSV file
   - Moves on to the next page

### Use Different Models
Try different Ollama models by selecting them in the dropdown:
- `llama3.2:1b`: Fastest, good for testing
- `llama3`: Better quality, slower
- `mistral`: Alternative model
- `gemma`: Another option

## Troubleshooting

### If Ollama Isn't Working
1. Make sure the Ollama server is running
2. Verify you've pulled the model you're trying to use
3. Check Ollama logs for any errors

### If Crawling Stops or Fails
1. Check your internet connection
2. Verify the website allows crawling
3. Try reducing the crawl speed (increase the sleep time)
4. Start with fewer pages

## License

[MIT License](LICENSE)
