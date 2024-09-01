from PyQt6.QtCore import QThread, pyqtSignal
import networkx as nx
import matplotlib.pyplot as plt
import os

class KnowledgeGraphGenerator(QThread):
    generation_progress = pyqtSignal(str)
    generation_complete = pyqtSignal(str)

    def __init__(self, analysis_results, output_dir):
        super().__init__()
        self.analysis_results = analysis_results
        self.output_dir = output_dir

    def run(self):
        self.generation_progress.emit("Generating knowledge graph...")
        
        G = nx.Graph()
        
        for file_path, data in self.analysis_results.items():
            G.add_node(file_path, **data)
        
        for file1 in G.nodes():
            for file2 in G.nodes():
                if file1 != file2:
                    shared_deps = set(G.nodes[file1]['dependencies']) & set(G.nodes[file2]['dependencies'])
                    if shared_deps:
                        G.add_edge(file1, file2, weight=len(shared_deps))

        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=8, font_weight='bold')
        
        output_file = os.path.join(self.output_dir, "knowledge_graph.png")
        plt.savefig(output_file)
        plt.close()
        
        self.generation_complete.emit(output_file)