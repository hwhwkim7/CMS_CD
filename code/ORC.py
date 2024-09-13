import networkx as nx
import time

from GraphRicciCurvature.FormanRicci import FormanRicci
from GraphRicciCurvature.OllivierRicci import OllivierRicci

print("\n- Import an example NetworkX karate club graph")
# G = nx.read_edgelist("dataset/polblogs/network.dat",nodetype=int)

# 빈 그래프 생성
G = nx.Graph()
# 여러 개의 노드 한 번에 추가
G.add_nodes_from(["A1", "A2", "A3", "A4", "B1","B2","B3","C1","C2","C3"])
# 여러 개의 엣지를 한 번에 추가
G.add_edges_from([("A1", "A2"), ("A1", "A3"),("A1", "A4"),("A2", "A3"),("A2", "A4"),("A3", "A4"),("B1", "B2"),("B1", "B3"),("B3", "B2"),("C1", "C2"),("C1", "C3"),("C3", "C2")])
# G.add_edges_from([("A4", "B1"),("B3", "C2")])
# G.add_edges_from([("B3", "C2")])


start_time = time.time()
print("\n===== Compute the Ollivier-Ricci curvature of the given graph G =====")
# compute the Ollivier-Ricci curvature of the given graph G
orc = OllivierRicci(G, alpha=0.5, verbose="INFO")
orc.compute_ricci_curvature()

end_time = time.time()
print("Time: %s seconds" % (end_time - start_time))

# get the edge in network
edge1, edge2 = list(G.edges())[0][1], list(G.edges())[0][0]
print(f"Karate Club Graph: The Ollivier-Ricci curvature of edge ({edge1},{edge2}) is %f" % orc.G[edge1][edge2]["ricciCurvature"] )

for u,v in G.edges():
    print((u,v), orc.G[u][v]["ricciCurvature"])

