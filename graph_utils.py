import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from urllib.parse import urlparse

def build_graph(adj_list):
    """
    Constructs a NetworkX DiGraph from an adjacency list.
    
    Args:
        adj_list (dict): Dictionary mapping URLs to a list of URLs they link to.
        
    Returns:
        nx.DiGraph: The constructed directed graph.
    """
    G = nx.DiGraph()
    for node, edges in adj_list.items():
        G.add_node(node)
        for edge in edges:
            G.add_edge(node, edge)
    return G

def visualize_graph(graph, ranks, show_subgraph=False, top_n=20):
    """
    Creates a visualization of the directed graph using Matplotlib.
    Nodes are sized and colored based on their PageRank score.
    
    Args:
        graph (nx.DiGraph): The network graph to visualize.
        ranks (dict): Dictionary mapping node URLs to their PageRank scores.
        show_subgraph (bool): If true, limits the graph visualization to top_n nodes.
        top_n (int): The number of top ranked nodes to show if show_subgraph is True.
        
    Returns:
        matplotlib.figure.Figure: The generated figure.
    """
    if not graph.nodes:
        return None

    # Determine if we filter down to a subgraph
    if show_subgraph and len(graph) > top_n:
        sorted_nodes = sorted(ranks.items(), key=lambda x: x[1], reverse=True)
        top_nodes = [node for node, rank in sorted_nodes[:top_n]]
        plot_graph = graph.subgraph(top_nodes)
    else:
        plot_graph = graph

    # Optional styling using Matplotlib
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Determine positions for nodes using a spring layout algorithm
    # k regulates distance, higher is further apart
    pos = nx.spring_layout(plot_graph, k=0.7, seed=42)
    
    # Node sizes based on rank score. Baseline 300 so smallest are visible.
    node_sizes = [300 + (ranks.get(node, 0) * 15000) for node in plot_graph.nodes()]
    
    # Node colors gradient based on rank
    node_colors = [ranks.get(node, 0) for node in plot_graph.nodes()]
    
    # Identify the absolute top node to highlight
    top_node = max(ranks, key=ranks.get) if ranks else None
        
    # Draw the edges (links between pages)
    nx.draw_networkx_edges(
        plot_graph, pos, 
        ax=ax, 
        arrows=True,
        arrowstyle='-|>',
        arrowsize=15,
        edge_color='gray',
        alpha=0.3,
        connectionstyle="arc3,rad=0.1"
    )
    
    # Draw all the nodes
    nodes = nx.draw_networkx_nodes(
        plot_graph, pos,
        ax=ax,
        node_size=node_sizes,
        node_color=node_colors,
        cmap=plt.cm.coolwarm, # Using coolwarm colormap for clear High/Low distinction
        alpha=0.9,
        edgecolors='white',
        linewidths=1.0
    )
    
    # Highlight the top node specifically with a distinct outline
    if top_node in plot_graph:
        nx.draw_networkx_nodes(
            plot_graph, pos,
            nodelist=[top_node],
            node_size=[300 + (ranks.get(top_node, 0) * 15000)],
            node_color=[ranks[top_node]],
            cmap=plt.cm.coolwarm,
            ax=ax,
            edgecolors='#ffd700', # Gold border
            linewidths=4
        )
    
    # Add a colorbar legend
    cbar = plt.colorbar(nodes, ax=ax, shrink=0.7)
    cbar.set_label('Calculated PageRank Score')
    
    # Make sensible short labels from the URL so they fit visually
    labels = {}
    for node in plot_graph.nodes():
        path = urlparse(node).path
        if not path or path == '/':
            # It's a root domain, perhaps just extract netloc or final part
            name = urlparse(node).netloc.split('.')[-2] if len(urlparse(node).netloc.split('.')) >= 2 else node
            labels[node] = name[:10]
        else:
            # It's a path, get the last sensible part
            parts = list(filter(None, path.split('/')))
            name = parts[-1] if parts else "root"
            labels[node] = name[:10]
                
    nx.draw_networkx_labels(
        plot_graph, pos, 
        labels=labels,
        font_size=9,
        font_color='black',
        font_weight='bold'
    )
    
    ax.set_title("Directed Web Graph Visualization\n(Node sizes scaled by Rank, Gold outline on Top Page)")
    ax.axis('off') # Hide the standard matplotlib axes
    
    plt.tight_layout()
    return fig

def display_results(ranks):
    """
    Transforms the ranking dictionary into a sorted Pandas DataFrame.
    
    Args:
        ranks (dict): Dictionary mapping URLs to PageRank scores.
        
    Returns:
        pd.DataFrame: A nice formatted table.
    """
    df = pd.DataFrame(list(ranks.items()), columns=['Page URL', 'PageRank Score'])
    df = df.sort_values(by='PageRank Score', ascending=False).reset_index(drop=True)
    df.index = df.index + 1
    df.index.name = 'Rank'
    return df
