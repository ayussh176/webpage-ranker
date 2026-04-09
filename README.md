# Web Page Ranking using PageRank Algorithm on Web Graph with Live URL Scraping

This project is an end-to-end Python system that scrapes a website, builds a directed web graph of its internal links, and algorithmically calculates the importance of each page using a custom implementation of the **PageRank algorithm** from scratch. It includes an interactive Streamlit frontend for dynamic user inputs, real-time scraping progress, graph visualization, and resulting tabular data.

## Features
- **Live URL Scraping**: Uses `requests` and `BeautifulSoup4` to perform a Breadth-First Search (BFS) starting from any given valid URL.
- **Scraping Limits**: Restricts scraping to the internal domain and allows a max depth limit to prevent infinite runtimes, ensuring swift UI responses.
- **Graph Construction**: Builds a reliable directed graph (`networkx.DiGraph`), with pages as nodes and hyperlinks as directed edges.
- **Custom PageRank**: Implements the mathematical PageRank formula from scratch without relying on NetworkX's built-in alternatives.
- **Beautiful UI**: Hosted on a smooth Streamlit dashboard with a customizable configuration sidebar.
- **Visual Analytics**: Utilizes `matplotlib` to render the web graph, uniquely scaling node size and coloring them corresponding to their rank score. Highlights the top ranked node dynamically.
- **Data Export**: Built-in Pandas dataframe visualizations that sort seamlessly with an added "Export to CSV" bonus feature.

## PageRank Algorithm Explanation

The PageRank algorithm measures the importance of website pages. According to Google, PageRank works by counting the number and quality of links to a page to determine a rough estimate of how important the website is. The underlying assumption is that more important websites are likely to receive more links from other websites.

Our custom implementation calculates the score iteratively using the following formula:

```text
PR(p) = (1 - d)/N + d * Σ (PR(q) / L(q))
```

Where:
- `PR(p)` is the resulting PageRank of node `p`.
- `d` is the **Damping Factor** (default is `0.85`). This represents the probability that a hypothetical random surfer continues clicking links rather than starting over completely.
- `N` is the total number of nodes in the graph.
- `q` represents the immediate predecessors of `p` (pages that hyperlink to `p`).
- `L(q)` represents the out-degree (number of outgoing links) of page `q`.

The algorithm iteratively distributes portions of each node's rank uniformly amongst its outgoing links. It repeats this standard distribution until convergence is achieved. Floating "dangling nodes" (pages with no outgoing links) are correctly handled by mathematically treating them as linking to all other pages uniformly, thus ensuring the sum total PageRank remains `1.0` and doesn't leak out of the system.

## Setup & Running the Project

**1. Install Required Dependencies:**
Navigate to the root directory where the files are stored and install everything via:
```bash
pip install -r requirements.txt
```

**2. Run the Streamlit Application:**
```bash
streamlit run app.py
```
This will launch the application server locally, typically accessible via `http://localhost:8501/` in your web browser. From there, you can enter any starting URL (such as `http://quotes.toscrape.com/`) to initiate the scraping and ranking phase.
