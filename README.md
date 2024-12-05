# EdgeTrader 
EdgeTrader 7.7 self-learning
 





This script implements a trading signals application using news scraping, sentiment analysis, and natural language processing (NLP). The app processes articles and generates trading signals (BUY, SELL, or NEUTRAL) based on sentiment, named entity recognition (NER), and keyword proximity. The app uses the VADER sentiment analysis tool, spaCy for NER, and BeautifulSoup for web scraping.

Key Features:
Web Scraping:

The app scrapes news articles from sources like CNBC.
It extracts article titles, links, and summaries.
Dynamic keywords from the articles are loaded and updated to improve analysis.
Sentiment Analysis:

VADER sentiment analysis is used to categorize the sentiment of news summaries as positive, negative, or neutral.
A weighted decision-making system is applied based on the sentiment and key phrases like "growth", "decline", "merger", etc.
Named Entity Recognition (NER):

SpaCy is used to identify named entities in the news articles (e.g., companies, products, or events).
This helps identify if the article mentions positive or negative entities (like "growth" or "decline").
Trade Decision Logic:

A decision is made based on the sentiment score and the presence of specific entities or keywords in the article.
If the sentiment is positive, the decision is to "BUY"; if negative, it's "SELL". If no clear sentiment, the decision is "NEUTRAL".
The logic also considers entity proximity to keywords (e.g., if "growth" is near "merger", it strengthens a "BUY" signal).
GUI:

The app uses Tkinter for its GUI, with a responsive design and a custom theme (Enterprise Blue).
It features a signal log to display trade decisions in real-time, and allows users to view past signals and saved articles.
The About and Help dialogs provide more information about the app's purpose and usage.
Persistence:

Trading signals, past signals, and dynamic keywords are saved in JSON files for persistence across sessions.
New keywords detected in articles are added to the dynamic keyword list.


Run the GUI: To use this program, you need to run the script, which will open the Tkinter GUI. You can then interact with it by clicking buttons to start analysis and view results.
Scraping and Analysis: When the analysis starts, the app will fetch articles, analyze them, and update the signal log with "BUY", "SELL", or "NEUTRAL" signals.
Expand Sources: You can add more news sources by expanding the sources list, which defines the URL and scraping parameters for each source.
Customize Keywords: The app loads dynamic keywords from a file, but you can also manually add more keywords to tailor it to your preferences.


you might need these
pip install nltk
python -m spacy download en_core_web_sm

From the Help file:
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
        
		
		



If you enjoy this program, buy me a coffee https://buymeacoffee.com/siglabo
You can use it free of charge or build upon my code. 
 
(c) Peter De Ceuster 2024
Software Distribution Notice: https://peterdeceuster.uk/doc/code-terms 
This software is released under the FPA General Code License.
 

 ![Screenshot 2024-12-05 045033](https://github.com/user-attachments/assets/38d1a04e-af58-414f-8347-b7261b292599)

