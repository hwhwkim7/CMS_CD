import networkx as nx
import time
import argparse

from GraphRicciCurvature.OllivierRicci import OllivierRicci

def remove_largest_negative_edge(C, orc):
    # Ollivier-Ricci curvature 계산 후 가장 큰 음수인 엣지를 탐색
    max_negative_edge = None
    max_negative_value = 0

    for u, v in C.edges():
        if orc.G[u][v]["ricciCurvature"] < max_negative_value:
            max_negative_edge = (u, v)
            max_negative_value = orc.G[u][v]["ricciCurvature"]


    if max_negative_edge is not None:
        C.remove_edge(*max_negative_edge)
        # print(f"Removed edge {max_negative_edge} with Ricci curvature {max_negative_value}")
        return C
    return None
# file_path = "dataset/syn/ds/d_avg_20"

def run(C):
    start_time = time.time()

    while True:
        orc = OllivierRicci(C, alpha=0.5, verbose="INFO")  # 다시 Ricci curvature를 계산
        orc.compute_ricci_curvature()

        if not remove_largest_negative_edge(C, orc):
            break

    communities = [list(component) for component in nx.connected_components(C)]
    end_time = time.time()
    return communities, end_time - start_time

