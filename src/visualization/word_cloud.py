from PyQt6.QtCore import QThread, pyqtSignal
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

class WordCloudGenerator(QThread):
    generation_progress = pyqtSignal(str)
    generation_complete = pyqtSignal(str)

    def __init__(self, analysis_results, output_dir, shape):
        super().__init__()
        self.analysis_results = analysis_results
        self.output_dir = output_dir
        self.shape = shape

    def run(self):
        self.generation_progress.emit("Generating word cloud...")
        
        text = " ".join(file_data.get('content', '') for file_data in self.analysis_results.values())
        
        if self.shape == "Rectangle":
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        elif self.shape == "Circle":
            mask = plt.imread("circle_mask.png")  # You need to provide this mask image
            wordcloud = WordCloud(width=800, height=800, background_color='white', mask=mask).generate(text)
        else:  # Custom shape
            mask = plt.imread("custom_mask.png")  # You need to provide this mask image
            wordcloud = WordCloud(width=800, height=800, background_color='white', mask=mask).generate(text)
        
        plt.figure(figsize=(10, 10))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        
        output_file = os.path.join(self.output_dir, "word_cloud.png")
        plt.savefig(output_file)
        plt.close()
        
        self.generation_complete.emit(output_file)