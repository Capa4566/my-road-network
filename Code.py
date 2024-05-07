import osmnx as ox
import networkx as nx
import random
import pandas as pd

# Download the road network
G = ox.graph_from_bbox(39.84, 39.97, 116.30, 116.46, network_type='drive')

# Calculate the length of each edge and add it as an attribute
for u, v, k, data in G.edges(keys=True, data=True):
    data['length'] = data.get('length', ox.distance.great_circle_vec(G.nodes[u]['y'], G.nodes[u]['x'], G.nodes[v]['y'], G.nodes[v]['x']))

# Get a random start and end node
nodes = list(G.nodes())
node1 = random.choice(nodes)
node2 = random.choice(nodes)

# Get the latitude and longitude of the start and end nodes
node1_lat_lon = (G.nodes[node1]['y'], G.nodes[node1]['x'])
node2_lat_lon = (G.nodes[node2]['y'], G.nodes[node2]['x'])

shortest_path = nx.shortest_path(G, node1, node2, weight='length')
length = nx.shortest_path_length(G, node1, node2, weight='length')

# FIGURE 1
# Project the graph
G_projected = ox.project_graph(G)

# Plot the graph
fig, ax = ox.plot_graph(G_projected, node_size=0, edge_color='grey', bgcolor='k', show=False, close=False)

# Plot the shortest path
path_edges = list(zip(shortest_path, shortest_path[1:]))
ox.plot.plot_graph_route(G_projected, shortest_path, route_color='r', route_linewidth=2, node_size=0, ax=ax)

# Plot the start and end nodes
node_positions = {node: (G_projected.nodes[node]['x'], G_projected.nodes[node]['y']) for node in shortest_path}
nx.draw_networkx_nodes(G_projected, pos=node_positions, ax=ax, nodelist=[node1, node2], node_color='blue', node_size=10)

# OUTPUT 1
# Print nodes and shortest path length
print("Node 1:", node1_lat_lon)
print("Node 2:", node2_lat_lon)
print("Shortest path length:", length, "m")

# Output the number of edges in the shortest path
print("Number of edges in the shortest path:", len(path_edges))

# Add 'edge_ID' attribute to each edge in the shortest path
edge_id = 1
for u, v in zip(shortest_path[:-1], shortest_path[1:]):
    G[u][v][0]['edge_ID'] = edge_id
    edge_id += 1

# TABLE 1 (edges and attributes table)
data_list = []
for u, v in path_edges:
    data = G[u][v][0]
    highway_type = data.get('highway', 'N/A')
    length = data.get('length', 'N/A')
    edge_id = data.get('edge_ID', 'N/A')
    data_list.append({"Edge ID": edge_id, "Highway Type": highway_type, "Length": length})

# Create a DataFrame from the data list
df = pd.DataFrame(data_list, columns=["Edge ID", "Highway Type", "Length"])

# TABLE 2
# Group edges by "Highway Type" and sum the lengths
grouped_df = df.groupby("Highway Type").agg({"Edge ID": lambda x: ', '.join(map(str, x)), "Length": "sum"})

# FIGURE 2
# Determine the bounding box of the shortest path
min_lat = min(G.nodes[node]['y'] for node in shortest_path)
max_lat = max(G.nodes[node]['y'] for node in shortest_path)
min_lon = min(G.nodes[node]['x'] for node in shortest_path)
max_lon = max(G.nodes[node]['x'] for node in shortest_path)

# Expand the bounding box to include surrounding nodes
buffer = 0.0005  # Adjust this value as needed
min_lat -= buffer
max_lat += buffer
min_lon -= buffer
max_lon += buffer

# Find nodes within the expanded bounding box
surrounding_nodes = [node for node in G.nodes() if min_lat <= G.nodes[node]['y'] <= max_lat and min_lon <= G.nodes[node]['x'] <= max_lon]

# Create a subgraph containing the shortest path and surrounding nodes
surrounding_graph = G.subgraph(surrounding_nodes)

# Project the subgraph
surrounding_graph_projected = ox.project_graph(surrounding_graph)
# Plot the subgraph
fig, ax = ox.plot_graph(surrounding_graph_projected, node_size=7, node_color='white', edge_color='white', edge_linewidth=0.2, bgcolor='black', show=False, close=False)
# Plot the shortest path
ox.plot.plot_graph_route(surrounding_graph_projected, shortest_path, route_color='r', route_linewidth=3, node_size=5, node_color='white', ax=ax)

# Output the DataFrame
df

# Output the grouped DataFrame
grouped_df