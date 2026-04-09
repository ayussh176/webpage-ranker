import streamlit as st
import pandas as pd
from scraper import scrape_links
from graph_utils import build_graph, visualize_graph, display_results
from pagerank import calculate_pagerank

# Configure the visual style and settings for the Streamlit page
st.set_page_config(page_title="PageRank Web Graph Scraper", page_icon="🕸️", layout="wide")

# Add some custom CSS for styling UI elements (glassmorphism/premium feel)
st.markdown("""
<style>
    .top-rank-box {
        background: linear-gradient(135deg, #1f4037 0%, #99f2c8 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        color: white;
        margin-bottom: 25px;
    }
    .top-rank-box a {
        color: white !important;
        font-weight: bold;
        text-decoration: underline;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🕸️ Web Page Ranking & Graph Visualization")
st.markdown("""
This application scrapes a website up to a specified limit, constructs a directed web graph of its internal links, 
and calculates the **PageRank** algorithm entirely from scratch to rank the most important pages.
""")

with st.sidebar:
    st.header("⚙️ Configuration")
    target_url = st.text_input("Enter Target URL:", placeholder="http://quotes.toscrape.com/")
    max_pages = st.slider("Max Pages to Scrape:", min_value=5, max_value=100, value=20)
    d_factor = st.slider("Damping Factor (d):", min_value=0.5, max_value=0.99, value=0.85, step=0.01)
    show_subgraph = st.checkbox("Only visualize Top 20 Nodes", value=False)
    
    st.markdown("---")
    run_btn = st.button("🚀 Scrape & Rank", type="primary", use_container_width=True)

if run_btn:
    if not target_url:
        st.error("Please enter a valid URL to begin. Make sure it includes http:// or https://")
    else:
        # 1. Scrape Links
        st.subheader("1. 🌐 Scraping Web Pages...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Callback to update the streamlit UI dynamically during scraping
        def update_progress(current, total):
            ratio = min(current / total, 1.0)
            progress_bar.progress(ratio)
            status_text.text(f"Scraped {current} / {total} pages...")
            
        try:
            with st.spinner("Initializing web scraper..."):
                adj_list = scrape_links(target_url, max_pages=max_pages, progress_callback=update_progress)
            status_text.text(f"✅ Scraping complete! Found {len(adj_list)} unique pages/nodes.")
            progress_bar.progress(1.0)
            
            if not adj_list:
                st.warning("No pages found or could not reach the server.")
                st.stop()
                
            # 2. Build Graph
            st.subheader("2. 🧠 Building Directed Graph...")
            with st.spinner("Constructing NetworkX Graph..."):
                G = build_graph(adj_list)
            st.info(f"Graph successfully created with **{G.number_of_nodes()}** nodes and **{G.number_of_edges()}** edges.")
            
            # 3. Calculate PageRank
            st.subheader("3. 🔢 Calculating PageRank (From Scratch)...")
            with st.spinner("Iterating PageRank formula..."):
                ranks = calculate_pagerank(G, d=d_factor)
            
            if not ranks:
                st.warning("Error computing ranks (Graph might be empty).")
                st.stop()
                
            st.success("✅ PageRank calculation converged!")
            
            # Identify Top Page
            top_page = max(ranks, key=ranks.get)
            top_score = ranks[top_page]
            
            # Show top page in a beautifully styled div
            st.markdown(f"""
            <div class="top-rank-box">
                <h2>🏆 Top Ranked Page</h2>
                <a href="{top_page}" target="_blank">{top_page}</a>
                <br>
                <p>Calculated Score: <b>{top_score:.4f}</b></p>
            </div>
            """, unsafe_allow_html=True)
            
            # 4. Display Results and Visualization
            col1, col2 = st.columns([1, 1.5])
            
            with col1:
                st.subheader("📊 Ranking Table")
                df_results = display_results(ranks)
                st.dataframe(df_results, use_container_width=True, height=500)
                
                # Bonus Feature: Export rankings to CSV
                csv = df_results.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Rankings as CSV",
                    data=csv,
                    file_name='pagerank_results.csv',
                    mime='text/csv',
                    use_container_width=True
                )
                
            with col2:
                st.subheader("📈 Web Graph Visualization")
                with st.spinner("Generating Matplotlib representation..."):
                    fig = visualize_graph(G, ranks, show_subgraph=show_subgraph, top_n=20)
                    if fig:
                        st.pyplot(fig)
                    else:
                        st.info("Graph is empty, nothing to visualize.")
                        
        except ValueError as ve:
            st.error(f"❌ Input Error: {ve}")
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {e}")
