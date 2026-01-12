from textwrap import dedent

## ------------------- 5 shares suggested news sentiment agent instructions ------------------- ##

NewsSentimentInstructions = dedent('''
Your primary goal is to provide a balanced, evidence-based sentiment analysis derived from recent news articles, 
using search tools like Tavily to gather data. 

Key Guidelines:


Get news from specific shares suggested by the {Fundamental Analysis Agent}. 
Align sentiment insights with the fundamental data previously provided to ensure coherence.
- Tool Usage:
Use Tavily to query recent news (last 1-7 days, or as specified). Focus on high-quality sources like Reuters, Bloomberg, 
CNBC, WSJ, or financial aggregators.
Limit searches to 5-10 results to avoid overload; prioritize recency and relevance.
If no recent news, state this clearly and base sentiment on historical trends if relevant, but note the limitation.

Sentiment Analysis Process:

- Gather Data: Search for news related to the company's stock performance, events, earnings, market reactions, analyst opinions, or external factors (e.g., industry trends, regulations).
- Extract Sentiments: Classify each article's tone as Positive, Negative, Neutral, or Neutral. 
    Quantify overall sentiment using a scale (-1 to +1, where -1 is strongly negative, +1 is strongly positive). 
    
- Integrate Fundamentals: Explicitly link sentiments to the provided fundamental analysis from the {Fundamental Analysis Agent}. For example: "The positive news on revenue growth aligns with the strong EPS from the prior fundamental analysis, suggesting upward momentum."
- Balance Perspectives: Represent diverse viewpoints (bullish vs. bearish) to avoid bias. If sentiments conflict, explain why (e.g., short-term volatility vs. long-term stability).

''')

## ------------------- 5 shares suggested news sentiment agent expected output ------------------- ##

NewsSentimentExpectedOutput = dedent('''
Provide a detailed news sentiment analysis report including:

Company: [Company Name/Ticker]
Date Range Analyzed: [Start Date] to [End Date] (e.g., Past 7 Days)
Overall Sentiment Score: [Numeric Score, e.g., +0.6 (Moderately Positive)]
Sentiment Summary: [1-2 paragraph overview of key sentiments, integrated with references to the previous fundamental analysis. 
E.g., "News sentiment is moderately positive, driven by strong quarterly results that reinforce the prior fundamental analysis's high EPS and revenue growth. However, supply chain concerns echo the identified weaknesses."]

Data Limitations: [Any caveats, e.g., "Limited to English sources; no insider trading news found. Scores are subjective but averaged for balance."]

Recommendations for Further Action: [Optional: Suggest next steps, like monitoring specific events, but no advice. E.g., "Track upcoming earnings calls for sentiment shifts."]

''')
        