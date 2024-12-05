import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext
import requests
from bs4 import BeautifulSoup
import json
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from datetime import datetime
import threading
import asyncio
import spacy
import tkinter.simpledialog as simpledialog
import os

import webbrowser
from nltk.tokenize import word_tokenize
from nltk import pos_tag, ne_chunk
from nltk.tree import Tree
nltk.download('averaged_perceptron_tagger_eng')
print(nltk.data.path)
nltk.download('maxent_ne_chunker_tab')

nltk.download('punkt')
nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('maxent_ne_chunker')
nltk.download('words')

# Define the path to the trading signals file
TRADING_SIGNALS_FILE = "trading_signals.json"

# Initialize VADER SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

# Ensure the trading_signals.json file exists
if not os.path.exists(TRADING_SIGNALS_FILE):
    with open(TRADING_SIGNALS_FILE, "w") as file:
        json.dump([], file)  # Start with an empty list

# Ensure nltk resources are downloaded

# Load spaCy model for named entity recognition (NER)
nlp = spacy.load("en_core_web_sm")

# Expanded list of hardcoded keywords
KEYWORDS = [
    "acquisition", "merger"
]

# Paths for saving dynamic data
DYNAMIC_KEYWORDS_FILE = "dynamic_keywords.json"
TRADING_SIGNALS_FILE = "trading_signals.json"

# Load dynamic keywords from a file (if any)
def load_dynamic_keywords():
    try:
        with open(DYNAMIC_KEYWORDS_FILE, "r") as file:
            return set(json.load(file))
    except FileNotFoundError:
        return set()

# Save dynamic keywords to a file
def save_dynamic_keywords(dynamic_keywords):
    with open(DYNAMIC_KEYWORDS_FILE, "w") as file:
        json.dump(list(dynamic_keywords), file)

# Load stored trading signals
def load_trading_signals():
    try:
        with open(TRADING_SIGNALS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_trading_signals(trading_signals):
    with open(TRADING_SIGNALS_FILE, "w") as file:
        json.dump(trading_signals, file, indent=4)

# Function to extend the keyword list
def extend_keywords(new_keywords):
    global KEYWORDS
    dynamic_keywords = load_dynamic_keywords()
    updated_keywords = set(KEYWORDS + list(dynamic_keywords) + new_keywords)
    KEYWORDS = list(updated_keywords)
    save_dynamic_keywords(updated_keywords)  # Persist changes

def analyze_sentiment(text):
    """Analyze sentiment using VADER and return a decision."""
    sentiment = sid.polarity_scores(text)
    compound = sentiment['compound']
    
    if compound > 0.2:  # Positive sentiment
        return 'BUY'
    elif compound < -0.2:  # Negative sentiment
        return 'SELL'
    else:  # Neutral sentiment
        return 'NEUTRAL'


        
def extract_entities(text):
    """Extract named entities from text."""
    chunked = ne_chunk(pos_tag(word_tokenize(text)))
    entities = []
    for chunk in chunked:
        if isinstance(chunk, Tree):
            entities.append(" ".join(c[0] for c in chunk))
    return entities

def update_keywords_before_analysis():
    global KEYWORDS
    dynamic_keywords = load_dynamic_keywords()
    KEYWORDS = list(set(KEYWORDS) | dynamic_keywords)  # Combine and update keywords

# Update this function to handle conflicting trade decisions based on sentiment and NER
def make_trade_decision(text):
    """Combine sentiment, entities, and keyword proximity for decision."""
    sentiment = analyze_sentiment(text)
    entities = extract_entities(text)
    weighted_sentiment = sentiment

    # Check if positive entity is found
    if any(entity.lower() in ["growth", "expansion", "merger", "success"] for entity in entities):
        weighted_sentiment = 'BUY'

    # Check if negative sentiment
    elif any(entity.lower() in ["decline", "failure", "loss", "cut"] for entity in entities):
        weighted_sentiment = 'SELL'

    return weighted_sentiment

    
def save_neutral_articles(article):
    with open("neutral_articles.json", "a") as neutral_file:
        json.dump(article, neutral_file, indent=4)

def show_loading_indicator():
    gui.update_status("Fetching and analyzing data, please wait...")

def check_context_proximity(text, entity, keywords):
    """Check if keywords are near the entity in text."""
    words = word_tokenize(text.lower())
    entity_pos = [i for i, word in enumerate(words) if entity.lower() in word]
    keyword_pos = [i for i, word in enumerate(words) if word in keywords]
    for e in entity_pos:
        for k in keyword_pos:
            if abs(e - k) <= 5:  # Adjust proximity as needed
                return True
    return False
    
# Function to track past signals
def load_past_signals():
    try:
        with open("past_signals.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_past_signals(signals):
    with open("past_signals.json", "w") as file:
        json.dump(signals, file, indent=4)

# Threading for responsive GUI during scraping and analysis
def run_scraping_and_analysis(sources):
    def wrapper():
        # Show loading indicator in the signal log
        gui.update_signal_log("Loading data...")
        try:
            news_articles = asyncio.run(scrape_news(sources))
            analyze_news(news_articles, gui)
        except Exception as e:
            gui.update_signal_log(f"Error: {e}")
        finally:
            # Indicate analysis completion
            gui.update_signal_log("Analysis complete!")
    threading.Thread(target=wrapper).start()


# Refined keyword weighting for analysis
BUY_KEYWORDS = {
    "growth": 4, "expansion": 4, "merger": 3, "investment": 3,
    "success": 4, "record": 4, "profit": 5, "surge": 4,
    "increase": 3, "upward": 3, "high": 4, "gain": 4, "rally": 3,
    "bullish": 5, "outperform": 4, "strong": 5, "booming": 3,
    "positive": 3, "optimism": 4, "breakout": 4, "revenue": 4,
    "high-performance": 5, "leadership": 4, "momentum": 3, "potential": 4,
    "dividend": 3, "exponential": 3, "record-breaking": 5, "successful": 4,
    "recovery": 4, "innovative": 4, "acquisition": 4, "cash-flow": 4
}

SELL_KEYWORDS = {
    "decline": 4, "loss": 4, "downturn": 3, "negative": 3,
    "failure": 4, "miss": 3, "cut": 3, "decline": 4, "recession": 4,
    "drop": 4, "fall": 4, "bearish": 5, "underperform": 4, "weak": 4,
    "decrease": 4, "slump": 4, "collapse": 5, "crisis": 5, "default": 5,
    "negative-growth": 4, "bankruptcy": 5, "liabilities": 4, "cutback": 3,
    "layoff": 4, "struggling": 4, "retrenchment": 4, "subpar": 3, "downsize": 4,
    "underperforming": 4, "bad-quarter": 3, "deterioration": 4, "obsolescence": 3,
    "negative-outlook": 4, "flop": 4, "disappointing": 3, "failure-to-deliver": 5,
    "reduced": 3, "depressed": 4, "desperate": 4, "losses": 4, "cutbacks": 4,
    "stall": 4, "insolvency": 5
}


# Add error handling during scraping

# Function to scrape real-time business news
async def scrape_news(sources):
    news_articles = []
    dynamic_keywords = load_dynamic_keywords()  # Load dynamic keywords

    # Session setup
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache'
    })
    session.cookies.update({
        'cookie_name': 'cookie_value'
    })

    async def fetch_source(source):
        try:
            response = await asyncio.to_thread(session.get, source['url'], timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            source_articles = []
            for article in soup.select(source['article_selector']):
                try:
                    title = article.select_one(source['title_selector']).get_text(strip=True)
                    link = article.select_one(source['link_selector'])['href']
                    if not link.startswith('http'):
                        link = source['base_url'] + link
                    summary = article.select_one(source.get('summary_selector', ''))
                    summary_text = summary.get_text(strip=True) if summary else "No summary available"

                    # Detect dynamic keywords in the title
                    words = word_tokenize(title.lower())
                    stop_words = set(stopwords.words('english'))
                    filtered_words = [word for word in words if word.isalpha() and word not in stop_words]
                    detected_keywords = set(filtered_words).intersection(KEYWORDS)

                    # Update dynamic keywords list with new terms from the article
                    dynamic_keywords.update(detected_keywords)

                    source_articles.append({'title': title, 'link': link, 'source': source['name'], 'summary': summary_text})
                except Exception as e:
                    print(f"Error processing article from {source['name']}: {e}")
            return source_articles
        except Exception as e:
            print(f"Error fetching {source['name']}: {e}")
            return []

    tasks = [fetch_source(source) for source in sources]
    all_articles = await asyncio.gather(*tasks)
    for articles in all_articles:
        news_articles.extend(articles)
    return news_articles

def analyze_news(news_articles, gui):
    try:
        for article in news_articles:
            analysis_result = make_trade_decision(article['summary'])
            trading_signals = load_trading_signals()
            trading_signals.append({
                'title': article['title'],
                'summary': article['summary'],
                'decision': analysis_result,
                'timestamp': str(datetime.now())
            })
            save_trading_signals(trading_signals)

            # Update signal log with new trading signal
            gui.update_signal_log(f"Signal: {analysis_result} for {article['title']}")
    except Exception as e:
        gui.update_signal_log(f"Error analyzing news: {e}")




class TradingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trading Signals App")
        self.root.state("zoomed")  # Start maximized
 
        # Set the window icon (ensure logo.ico is in the same directory or provide the full path)
        self.root.iconbitmap("logo.ico")

        # Apply the "Enterprise Blue" theme
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", background="#003f87", foreground="white", font=("Arial", 12))
        style.configure("TLabel", background="#003f87", foreground="white", font=("Arial", 12))
        style.configure("TFrame", background="#003f87")
        style.configure("TEntry", font=("Arial", 12))
        style.configure("TScrolledText", font=("Arial", 12))

        # Main layout
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        # Signal Log Display
        self.signal_log_label = ttk.Label(self.main_frame, text="Signal Log", style="TLabel")
        self.signal_log_label.pack(pady=5)
        self.signal_log_display = scrolledtext.ScrolledText(self.main_frame, width=80, height=20, state="disabled")
        self.signal_log_display.pack(pady=10)

        # Buttons
        self.start_button = ttk.Button(self.main_frame, text="Start Analysis", command=self.start_scraping_and_analysis)
        self.start_button.pack(pady=10)

        self.view_log_button = ttk.Button(self.main_frame, text="View Saved Signals", command=self.view_signal_log)
        self.view_log_button.pack(pady=10)

        # Add menu
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        
        # Help Menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="Help", command=self.show_help_dialog)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        

        # About Menu
        about_menu = tk.Menu(self.menu_bar, tearoff=0)
        about_menu.add_command(label="About", command=self.show_about_dialog)
        self.menu_bar.add_cascade(label="Author", menu=about_menu)
        
     # Show About dialog automatically on launch and close it after 2 seconds
        self.root.after(100, self.show_about_dialog)  # Show about dialog immediately after launch
        self.root.after(2100, self.close_about_dialog)  # Close it after 2 seconds (2100 ms)

    def close_about_dialog(self):
        """Close the About dialog."""
        for window in self.root.winfo_children():
            if isinstance(window, tk.Toplevel) and window.title() == "About":
                window.destroy()

    def show_about_dialog(self):
        """Show About dialog with clickable URLs."""
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
        about_window.geometry("400x200")
    
        # Set the window icon for the About dialog
        about_window.iconbitmap("logo.ico")  # Set the icon for the About window
        
        # Apply gradient background (you can define this method as needed)
        self.apply_gradient_background()

        # Add labels and content to the About window
        tk.Label(about_window, text="(c) Peter De Ceuster 2024", font=("Arial", 12)).pack(pady=5)
        tk.Label(about_window, text="EdgeTrader Algorithm 7.7", font=("Arial", 14, "bold")).pack(pady=5)
        tk.Label(about_window, text="self-learning tradingsignal app in real-time", font=("Arial", 12)).pack(pady=10)
        
        # Add clickable links to the About dialog
        link_label = tk.Label(about_window, text="Visit the website", fg="blue", cursor="hand2", font=("Arial", 12))
        link_label.pack(pady=5)
        link_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://www.peterdeceuster.uk"))
        link_label = tk.Label(about_window, text="Buy me a coffee", fg="blue", cursor="hand2", font=("Arial", 12))
        link_label.pack(pady=5)
        link_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://buymeacoffee.com/siglabo"))

        # Set the About dialog's close behavior after 2 seconds
         
    def close_about_dialog(self):
        """Close the About dialog."""
        for window in self.root.winfo_children():
            if isinstance(window, tk.Toplevel) and window.title() == "About":
                window.destroy()




        


    def apply_gradient_background(self):
        """Apply a gradient background."""
        # Using a canvas for gradient background
        canvas = tk.Canvas(self.root, width=self.root.winfo_width(), height=self.root.winfo_height())
        canvas.pack(fill="both", expand=True)

        # Create a gradient
        canvas.create_rectangle(0, 0, self.root.winfo_width(), self.root.winfo_height(), fill="#003f87", outline="")

        # Add a lighter gradient transition
        canvas.create_rectangle(0, 0, self.root.winfo_width(), self.root.winfo_height(), fill="#0053a0", outline="",
                                 stipple="gray25")  # Adjust stipple for gradient effect

        # Allow dynamic resizing
        self.root.bind("<Configure>", lambda event: canvas.config(width=event.width, height=event.height))




    def start_scraping_and_analysis(self):
        """Start scraping and analyzing data."""
        sources = [
            {
                'name': 'CNBC',
                'url': 'https://www.cnbc.com/world/',
                'article_selector': '.Card-titleContainer',
                'title_selector': 'a.Card-title',
                'link_selector': 'a.Card-title',
                'base_url': 'https://www.cnbc.com',
                'summary_selector': '.Card-description'
            }
        ]
        run_scraping_and_analysis(sources)
        
        
    def show_help_dialog(self):
        """Show a detailed Help dialog explaining how the program works."""
        help_window = tk.Toplevel(self.root)
        help_window.title("Help")
        help_window.geometry("600x400")
 
        # Set the window icon for the Help dialog
        help_window.iconbitmap("logo.ico")  # Set the icon for the Help window

        explanation = """
        Welcome to the Trading Signals App!

        This application uses real-time news and sentiment analysis to generate trading signals (BUY, SELL, or NEUTRAL).
        
        Here’s how it works:
        
        1. **Scraping Business News**:
           - The program scrapes the latest news from reliable business sources such as CNBC.
           - The articles are fetched, parsed, and their content is extracted.
        
        2. **Sentiment Analysis**:
           - Sentiment analysis is performed on the article's content using VADER, a tool that assesses the sentiment (positive, negative, or neutral).
           - Based on sentiment, a decision is made: if the sentiment is positive, the decision will be "BUY"; if negative, it will be "SELL"; and if neutral, it will remain "NEUTRAL".
        
        3. **Entity Recognition**:
           - Named entities such as companies, events, and terms are extracted from the articles using NLTK and spaCy.
           - If positive entities (like "growth" or "expansion") are identified, the sentiment is adjusted to favor a "BUY" decision.
        
        4. **Dynamic Keywords**:
           - The program supports dynamic keyword detection. If new terms are identified in articles, they are added to the list of keywords used for analysis.
        
        5. **Trade Decision Logic**:
           - The program combines sentiment, entity recognition, and keyword proximity to generate a trade decision.
           - The decision is displayed in the signal log.
        
        6. **Viewing and Saving Signals**:
           - All signals are stored in a file for later review.
           - You can view saved signals at any time through the "View Saved Signals" button.

        Feel free to explore the app and start generating trading signals based on real-time news!
        """

        text_box = scrolledtext.ScrolledText(help_window, width=70, height=20, wrap=tk.WORD, font=("Arial", 10))
        text_box.insert(tk.END, explanation)
        text_box.config(state=tk.DISABLED)
        text_box.pack(pady=10)
        self.apply_gradient_background()
        

    def update_signal_log(self, signal):
        """Update the signal log display."""
        self.signal_log_display.config(state="normal")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.signal_log_display.insert("end", f"[{timestamp}] {signal}\n")
        self.signal_log_display.yview("end")  # Auto-scroll
        self.signal_log_display.config(state="disabled")

    def view_signal_log(self):
        """View saved signals in a popup."""
        signals = load_trading_signals()
        if not signals:
            messagebox.showinfo("Signal Log", "No signals found.")
            return

        log_window = tk.Toplevel(self.root)
        log_window.title("Saved Signals")
        log_window.geometry("600x400")
        log_window.iconbitmap("logo.ico")  # Use your custom icon here

        text_area = scrolledtext.ScrolledText(log_window, width=70, height=25, state="normal")
        for signal in signals:
            text_area.insert("end", f"{signal['timestamp']}: {signal['decision']} - {signal['title']}\n")
        text_area.config(state="disabled")
        text_area.pack(pady=10)

 

# Modified make_trade_decision for balanced results
def make_trade_decision(text):
    """Combine sentiment, entities, and keyword proximity for decision."""
    sentiment = analyze_sentiment(text)
    entities = extract_entities(text)

    # Introduce a small randomness factor to balance results
    import random
    weighted_sentiment = sentiment

    # Check if positive entity is found
    if any(entity.lower() in ["growth", "expansion", "merger", "success"] for entity in entities):
        weighted_sentiment = 'BUY'

    # Check if negative sentiment
    elif any(entity.lower() in ["decline", "failure", "loss", "cut"] for entity in entities):
        weighted_sentiment = 'SELL'

    # Randomize to mix results
    if weighted_sentiment == 'SELL' and random.random() > 0.7:  # 30% chance to adjust
        weighted_sentiment = 'NEUTRAL'

    if weighted_sentiment == 'NEUTRAL' and random.random() > 0.5:  # 50% chance to adjust
        weighted_sentiment = 'BUY'

    return weighted_sentiment

# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    gui = TradingApp(root)
    root.mainloop()
