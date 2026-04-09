def calculate_pagerank(graph, d=0.85, max_iter=100, tol=1e-6):
    """
    Calculates PageRank score for nodes in a directed graph from scratch.
    
    Formula: PR(p) = (1 - d)/N + d * Σ (PR(q) / L(q))
    where q are pages linking to p, and L(q) is outgoing links from q.
    
    Args:
        graph (nx.DiGraph): The directed graph containing the nodes and edges.
        d (float): Damping factor, usually 0.85.
        max_iter (int): Maximum number of iterations to perform.
        tol (float): Tolerance for determining convergence.
        
    Returns:
        dict: A dictionary mapping node URLs to their finalized PageRank score.
    """
    nodes = list(graph.nodes())
    N = len(nodes)
    
    if N == 0:
        return {}
        
    # Initialize all nodes equally with 1/N
    pr = {node: 1/N for node in nodes}
    
    # Calculate outgoing links count L(q) for all q beforehand for efficiency
    out_degree = {node: len(list(graph.successors(node))) for node in nodes}
    
    # Identify dangling nodes (nodes with no out-links).
    # Without handling them, the PageRank score slowly leaks out of the system.
    # Standard practice is to treat them as linking to all other pages.
    dangling_nodes = [node for node in nodes if out_degree[node] == 0]
    
    for iteration in range(max_iter):
        new_pr = {}
        diff = 0
        
        # Calculate the sum of PRs of dangling nodes uniformly distributed
        dangling_sum = sum(pr[node] for node in dangling_nodes)
        
        for p in nodes:
            # Sum (PR(q) / L(q)) for all q linking to p
            in_sum = 0
            for q in graph.predecessors(p):
                in_sum += pr[q] / out_degree[q]
                
            # Full formula: handles standard incoming links + the portion distributed from dangling nodes
            new_pr[p] = (1 - d) / N + d * (in_sum + dangling_sum / N)
            
            # calculate difference to track convergence
            diff += abs(new_pr[p] - pr[p])
            
        pr = new_pr # Update pageranks for the next iteration
        
        if diff < tol:
            print(f"PageRank converged at iteration {iteration+1}")
            break
            
    # Final Normalize to ensure all PageRank scores sum to exactly 1.0
    # (Sometimes minor floating point arithmetic drifts occur)
    total_pr = sum(pr.values())
    if total_pr > 0:
        pr = {k: v/total_pr for k, v in pr.items()}
            
    return pr
