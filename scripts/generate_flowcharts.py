import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import os

# Set style
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

def create_flowchart_1():
    """
    Figure 1: Conceptual Framework / Taxonomy of Multilingual Reliability
    Decomposed into four interacting layers feeding into Multilingual Reliability.
    """
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    ax.set_xlim(-1, 9)
    ax.set_ylim(-7.5, 2)
    ax.axis('off')

    colors = {
        'blue':   {'fill': '#E3F2FD', 'edge': '#1976D2', 'text': '#0D47A1'},
        'green':  {'fill': '#E8F5E9', 'edge': '#388E3C', 'text': '#1B5E20'},
        'orange': {'fill': '#FFF3E0', 'edge': '#F57C00', 'text': '#E65100'},
        'red':    {'fill': '#FFEBEE', 'edge': '#D32F2F', 'text': '#B71C1C'},
        'gray':   {'fill': '#ECEFF1', 'edge': '#37474F', 'text': '#212121'},
    }

    bw, bh = 3.6, 1.4

    nodes = {
        'data': (1.8, 0.5),
        'eval': (6.2, 0.5),
        'gen':  (1.8, -2.5),
        'ctrl': (6.2, -2.5),
        'rel':  (4.0, -5.6),
    }

    boxes = {
        'data': ('Language & Data\nResources', 'blue', (bw, bh)),
        'eval': ('Evaluation\nMethodology', 'green', (bw, bh)),
        'gen':  ('Generation &\nGrounding', 'orange', (bw, bh)),
        'ctrl': ('Application-Level\nQuality Control', 'red', (bw, bh)),
        'rel':  ('Multilingual Reliability\n(Primary Evaluation Target)', 'gray', (4.8, 1.4)),
    }

    for name, (label, color_key, (w, h)) in boxes.items():
        cx, cy = nodes[name]
        c = colors[color_key]
        rect = patches.FancyBboxPatch(
            (cx - w/2, cy - h/2), w, h,
            boxstyle="round,pad=0.1,rounding_size=0.15",
            facecolor=c['fill'],
            edgecolor=c['edge'],
            linewidth=2.2,
            zorder=3
        )
        ax.add_patch(rect)
        weight = 'bold' if name == 'rel' else 'semibold'
        fontsize = 12 if name == 'rel' else 11.5
        ax.text(cx, cy, label, ha='center', va='center',
                fontsize=fontsize, fontweight=weight, color=c['text'], zorder=4)

    def draw_arrow(p1, p2, rad=0.0):
        connectionstyle = f"arc3,rad={rad}" if rad != 0 else "arc3,rad=0"
        ax.annotate(
            '', xy=p2, xytext=p1,
            arrowprops=dict(
                arrowstyle='-|>',
                color='#37474F',
                lw=2.0,
                mutation_scale=18,
                shrinkA=3, shrinkB=3,
                connectionstyle=connectionstyle
            ),
            zorder=2
        )

    # Inter-layer connections
    draw_arrow((nodes['data'][0] + bw/2, nodes['data'][1]),
               (nodes['eval'][0] - bw/2, nodes['eval'][1]))
    draw_arrow((nodes['data'][0], nodes['data'][1] - bh/2),
               (nodes['gen'][0], nodes['gen'][1] + bh/2))
    draw_arrow((nodes['eval'][0], nodes['eval'][1] - bh/2),
               (nodes['ctrl'][0], nodes['ctrl'][1] + bh/2))
    draw_arrow((nodes['gen'][0] + bw/2, nodes['gen'][1]),
               (nodes['ctrl'][0] - bw/2, nodes['ctrl'][1]))

    # Outer feeds into Multilingual Reliability
    draw_arrow((nodes['data'][0] - bw/2 + 0.3, nodes['data'][1] - bh/2),
               (nodes['rel'][0] - 2.4, nodes['rel'][1] + 0.3), rad=0.22)
    draw_arrow((nodes['eval'][0] + bw/2 - 0.3, nodes['eval'][1] - bh/2),
               (nodes['rel'][0] + 2.4, nodes['rel'][1] + 0.3), rad=-0.22)

    # Inner feeds into Multilingual Reliability
    draw_arrow((nodes['gen'][0] + 0.5, nodes['gen'][1] - bh/2),
               (nodes['rel'][0] - 1.2, nodes['rel'][1] + 0.7))
    draw_arrow((nodes['ctrl'][0] - 0.5, nodes['ctrl'][1] - bh/2),
               (nodes['rel'][0] + 1.2, nodes['rel'][1] + 0.7))

    plt.title("Figure 1: Conceptual Framework & Taxonomy of Multilingual Reliability",
              fontsize=14.5, fontweight='bold', pad=25, color='#212121')
    ax.text(4.0, 1.45, "Reliability decomposed into four interacting layers feeding into system evaluation",
            ha='center', va='center', fontsize=10, style='italic', color='#616161')

    plt.tight_layout()
    png_path = "flowchart1_conceptual_framework.png"
    jpg_path = "flowchart1_conceptual_framework.jpg"
    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    img = Image.open(png_path).convert('RGB')
    img.save(jpg_path, 'JPEG', quality=95)
    img.save(os.path.join("reports", "figures", jpg_path), 'JPEG', quality=95)
    if os.path.exists(png_path):
        os.remove(png_path)
    print(f"Generated {jpg_path}")


def create_flowchart_2():
    """
    Figure 2: End-to-End System Pipeline Flowchart
    Faithful recreation of the paper's TikZ pipeline flowchart with orthogonal, clean routing.
    """
    fig, ax = plt.subplots(figsize=(15, 15), dpi=300)
    ax.set_xlim(-0.5, 14.5)
    ax.set_ylim(-13.5, 1.5)
    ax.axis('off')

    c_start  = {'fill': '#ECEFF1', 'edge': '#455A64', 'text': '#263238'}
    c_proc   = {'fill': '#E3F2FD', 'edge': '#1E88E5', 'text': '#0D47A1'}
    c_api    = {'fill': '#E0F2F1', 'edge': '#00897B', 'text': '#004D40'}
    c_arm    = {'fill': '#EDE7F6', 'edge': '#5E35B1', 'text': '#311B92'}
    c_res    = {'fill': '#E8F5E9', 'edge': '#2E7D32', 'text': '#1B5E20'}

    def draw_box(cx, cy, w, h, title, subtitle="", style='proc', dashed=False):
        if style == 'start':
            c = c_start
        elif style == 'api':
            c = c_api
        elif style == 'arm':
            c = c_arm
        elif style == 'result':
            c = c_res
        else:
            c = c_proc

        ls = '--' if dashed else '-'
        rect = patches.FancyBboxPatch(
            (cx - w/2, cy - h/2), w, h,
            boxstyle="round,pad=0.08,rounding_size=0.12",
            facecolor=c['fill'],
            edgecolor=c['edge'],
            linewidth=2.0 if not dashed else 1.8,
            linestyle=ls,
            zorder=3
        )
        ax.add_patch(rect)
        if subtitle:
            ax.text(cx, cy + 0.16, title, ha='center', va='center',
                    fontsize=10.5, fontweight='bold', color=c['text'], zorder=4)
            ax.text(cx, cy - 0.22, subtitle, ha='center', va='center',
                    fontsize=8.5, fontstyle='italic', color=c['text'], zorder=4)
        else:
            ax.text(cx, cy, title, ha='center', va='center',
                    fontsize=10.5, fontweight='bold', color=c['text'], zorder=4)
        return (cx, cy, w, h)

    def draw_straight_arrow(p1, p2, dashed=False, color='#37474F'):
        ls = '--' if dashed else '-'
        ax.annotate(
            '', xy=p2, xytext=p1,
            arrowprops=dict(
                arrowstyle='-|>',
                color=color,
                lw=1.8 if not dashed else 1.5,
                linestyle=ls,
                mutation_scale=16,
                shrinkA=2, shrinkB=2,
                connectionstyle="arc3,rad=0"
            ),
            zorder=2
        )

    def draw_elbow_arrow(p1, p2, color='#37474F', orientation='horizontal_first', rad=0.08, dashed=False):
        style = f"angle,angleA=0,angleB=90,rad={rad*10}" if orientation == 'horizontal_first' else f"angle,angleA=90,angleB=0,rad={rad*10}"
        ls = '--' if dashed else '-'
        ax.annotate(
            '', xy=p2, xytext=p1,
            arrowprops=dict(
                arrowstyle='-|>',
                color=color,
                lw=1.8 if not dashed else 1.5,
                linestyle=ls,
                mutation_scale=16,
                shrinkA=2, shrinkB=2,
                connectionstyle=style
            ),
            zorder=2
        )

    col1 = 1.9
    col2 = 5.7
    col3 = 9.5
    col4 = 12.8

    # --- ROW 1: Data Sources ---
    y1 = 0.0
    draw_box(col1, y1, 3.4, 0.9, "BEIR SciFact Dataset", "Official UKP URL", style='start')
    draw_box(col2, y1, 3.5, 0.9, "5,183 English Abstracts", "PubMed / bioRxiv Corpus", style='proc')
    draw_box(col3, y1, 3.4, 0.9, "300 Test Claims", "English Ground-Truth", style='proc')

    draw_straight_arrow((col1 + 1.7, y1), (col2 - 1.75, y1))
    draw_straight_arrow((col2 + 1.75, y1), (col3 - 1.7, y1))

    # --- ROW 2: Translation & Corpus Indexing ---
    y2 = -1.6
    draw_box(col1, y2, 3.4, 0.9, "Corpus Indexing", "Tokenization & Embeddings", style='proc')
    draw_box(col3, y2, 3.4, 0.9, "Hindi Query Translation", "Parallel Cross-Lingual Setup", style='proc')
    draw_box(col4, y2 + 0.35, 2.7, 0.65, "MyMemory API", "89 queries (API)", style='api', dashed=True)
    draw_box(col4, y2 - 0.45, 2.7, 0.75, "OPUS-MT (Helsinki)", "211 queries (HF)", style='api', dashed=True)

    draw_straight_arrow((col1, y1 - 0.45), (col1, y2 + 0.45))
    draw_straight_arrow((col3, y1 - 0.45), (col3, y2 + 0.45))
    
    draw_straight_arrow((col4 - 1.35, y2 + 0.35), (col3 + 1.7, y2 + 0.15), dashed=True, color='#00796B')
    draw_straight_arrow((col4 - 1.35, y2 - 0.45), (col3 + 1.7, y2 - 0.15), dashed=True, color='#00796B')

    # --- ROW 3: Three Retrieval Arms ---
    y3 = -3.7
    draw_box(col1, y3, 3.4, 1.0, "BM25 Retriever", "rank-bm25 / BM25Okapi", style='arm')
    draw_box(col2, y3, 3.5, 1.0, "EN-Dense Retriever", "HF: all-MiniLM-L6-v2", style='arm')
    draw_box(col3, y3, 3.4, 1.0, "Multi-Dense Retriever", "paraphrase-multilingual-L12", style='arm')

    # Offline HF Cache Hub
    y_cache = -5.0
    draw_box(7.6, y_cache, 4.6, 0.75, "HuggingFace Model Hub Cache", "Cached offline inference", style='api', dashed=True)

    draw_straight_arrow((col1, y2 - 0.45), (col1, y3 + 0.5))
    draw_elbow_arrow((col1 + 0.5, y2 - 0.45), (col2, y3 + 0.5), orientation='vertical_first')
    draw_elbow_arrow((col1 + 1.0, y2 - 0.45), (col3 - 0.5, y3 + 0.5), orientation='vertical_first')

    draw_elbow_arrow((col2 + 0.6, y_cache + 0.37), (col2, y3 - 0.5), dashed=True, color='#00796B', orientation='vertical_first')
    draw_elbow_arrow((col3 - 0.6, y_cache + 0.37), (col3, y3 - 0.5), dashed=True, color='#00796B', orientation='vertical_first')

    # --- ROW 4: Query Fan-in ---
    y4 = -6.4
    draw_box(2.6, y4, 3.8, 0.85, "English Queries", "300 Original Claims", style='proc')
    draw_box(8.8, y4, 3.8, 0.85, "Hindi Queries", "human_checked = False", style='proc')

    # Route English queries from claims down along left edge
    ax.annotate(
        '', xy=(2.6, y4 + 0.42), xytext=(col3 - 1.7, y1 - 0.2),
        arrowprops=dict(
            arrowstyle='-|>',
            color='#37474F',
            lw=1.8,
            mutation_scale=16,
            shrinkA=2, shrinkB=2,
            connectionstyle="angle,angleA=-90,angleB=180,rad=10"
        ),
        zorder=2
    )

    # Translation -> Hindi Queries
    draw_straight_arrow((8.8, y2 - 0.45), (8.8, y4 + 0.42))

    # --- ROW 5: Ranked Results ---
    y5 = -8.1
    draw_box(5.7, y5, 5.8, 0.9, "Top-10 Ranked Results", "per query × 3 retrieval methods", style='proc')

    draw_elbow_arrow((col1, y3 - 0.5), (4.0, y5 + 0.45), orientation='vertical_first')
    draw_straight_arrow((col2, y3 - 0.5), (col2, y5 + 0.45))
    draw_elbow_arrow((col3, y3 - 0.5), (7.4, y5 + 0.45), orientation='vertical_first')

    draw_straight_arrow((2.6, y4 - 0.42), (4.7, y5 + 0.45))
    draw_straight_arrow((8.8, y4 - 0.42), (6.7, y5 + 0.45))

    # --- ROW 6: Evaluation ---
    y6 = -9.7
    draw_box(4.5, y6, 4.8, 0.9, "Metric Computation", "Recall@1, Recall@5, Recall@10, MRR@10", style='proc')
    draw_box(9.5, y6, 3.8, 0.85, "scripts/validate_metrics.py", "Independent recompute audit", style='api', dashed=True)

    draw_straight_arrow((5.7, y5 - 0.45), (4.5, y6 + 0.45))
    draw_straight_arrow((9.5 - 1.9, y6), (4.5 + 2.4, y6), dashed=True, color='#00796B')

    # --- ROW 7: Publication Outputs ---
    y7 = -11.4
    draw_box(2.2, y7, 3.8, 0.9, "results/*.csv", "retrieval & query-level metrics", style='result')
    draw_box(6.8, y7, 3.8, 0.9, "4 Publication Figures", "reports/figures/ (PNG/JPG)", style='result')
    draw_box(11.4, y7, 3.6, 0.9, "Draft Paper", "paper/main.tex", style='result')

    draw_elbow_arrow((3.5, y6 - 0.45), (2.2, y7 + 0.45), orientation='vertical_first')
    draw_straight_arrow((4.1, y7), (4.9, y7))
    draw_straight_arrow((8.7, y7), (9.6, y7))

    # Title & Legend
    plt.title("Figure 2: End-to-End Multilingual Retrieval Evaluation Pipeline",
              fontsize=15, fontweight='bold', pad=25, color='#212121')
    ax.text(6.8, 1.1, "Flowchart showing dataset preparation, query translation, retrieval models, evaluation, and reporting",
            ha='center', va='center', fontsize=10.5, style='italic', color='#616161')

    # Legend at bottom
    leg_y = -12.7
    rect_leg = patches.FancyBboxPatch(
        (1.2, leg_y - 0.45), 11.2, 0.9,
        boxstyle="round,pad=0.08,rounding_size=0.1",
        facecolor='#F5F5F5',
        edgecolor='#BDBDBD',
        linewidth=1.2,
        zorder=1
    )
    ax.add_patch(rect_leg)
    ax.text(1.6, leg_y, "Legend:", fontsize=9.5, fontweight='bold', color='#424242', va='center')

    draw_straight_arrow((2.7, leg_y), (3.7, leg_y), color='#37474F')
    ax.text(3.9, leg_y, "Data Flow", fontsize=9, va='center', color='#37474F')

    draw_straight_arrow((5.5, leg_y), (6.5, leg_y), dashed=True, color='#00796B')
    ax.text(6.7, leg_y, "API / Tool Dependency", fontsize=9, va='center', color='#004D40')

    ax.text(9.5, leg_y, "(* Hindi: human_checked=False)", fontsize=8.5, fontstyle='italic', va='center', color='#D84315')

    plt.tight_layout()
    png_path = "flowchart2_system_pipeline.png"
    jpg_path = "flowchart2_system_pipeline.jpg"
    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    img = Image.open(png_path).convert('RGB')
    img.save(jpg_path, 'JPEG', quality=95)
    img.save(os.path.join("reports", "figures", jpg_path), 'JPEG', quality=95)
    if os.path.exists(png_path):
        os.remove(png_path)
    print(f"Generated {jpg_path}")

if __name__ == "__main__":
    create_flowchart_1()
    create_flowchart_2()
