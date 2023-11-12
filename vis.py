import os
import sqlite3
import networkx as nx
import plotly.graph_objects as go

# Define constants for database paths
DB_DIRECTORY = "./public/db"
DB_FILE = "requirements.db"

# Helper function to create edges for the plot
def make_edge(x, y, text, width):
    return go.Scatter(
        x=x,
        y=y,
        line=dict(width=width),
        hoverinfo='text',
        text=([text]),
        mode='lines')

# Function to construct the graph from the similarity data
def construct_graph(similarity_data):
    G = nx.Graph()
    for record in similarity_data:
        spec1 = (record['spec1_id'], {'label': record['spec1_name'] + ' ' + record['spec1_version']})
        spec2 = (record['spec2_id'], {'label': record['spec2_name'] + ' ' + record['spec2_version']})
        similarity_count = record['similarity_count']

        G.add_node(spec1[0], label=spec1[1]['label'])
        G.add_node(spec2[0], label=spec2[1]['label'])
        G.add_edge(spec1[0], spec2[0], weight=similarity_count)
    return G

# Function to create traces for Plotly visualization
def create_traces(G, pos):
    edge_trace = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        text = f"{G.nodes[edge[0]]['label']} -- {G.nodes[edge[1]]['label']}: {G[edge[0]][edge[1]]['weight']}"
        trace = make_edge([x0, x1, None], [y0, y1, None], text, width=G[edge[0]][edge[1]]['weight']*0.5)
        edge_trace.append(trace)

    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        textposition="top center",
        mode='markers+text',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Anzahl der Ähnlichkeiten',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['marker']['color'] += tuple([len(G.edges(node))])
        node_info = G.nodes[node]['label']
        node_trace['text'] += tuple([node_info])
    
    return edge_trace, node_trace

# Main function to run the graph construction and visualization
def main():
    db_path = os.path.join(DB_DIRECTORY, DB_FILE)
    
    # Use a context manager to ensure the database connection is closed properly
    with sqlite3.connect(db_path) as conn:
        # Assuming DataReader is defined elsewhere and works as expected
        from data_importer.controller.DataReader import DataReader
        data_reader = DataReader(conn)
        similarity_data = data_reader.get_similarity_counts()

    G = construct_graph(similarity_data)
    pos = nx.spring_layout(G, k=0.15, iterations=20)
    edge_trace, node_trace = create_traces(G, pos)

    # Define the layout for the visualization
    layout = go.Layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

    # Create the figure with the specified layout and traces
    fig = go.Figure(data=edge_trace + [node_trace], layout=layout)

    # Display the figure
    fig.show()

if __name__ == "__main__":
    main()
