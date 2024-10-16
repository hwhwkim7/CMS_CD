import copy
import numpy as np
import networkx as nx
import time
from GraphRicciCurvature.OllivierRicci import OllivierRicci

class Cluster:
    def __init__(self, cluster_id, nodes, G, O, edges=[], orc=0):
        self.c_id = cluster_id
        self.nodes = set(nodes)
        self.edges = edges
        self.d = 0
        self.orc = orc
        for u in self.nodes:
            self.d += G.degree(u)
            for v in self.nodes-{u}:
                if G.has_edge(u,v):
                    edge = (min(u,v), max(u,v))
                    if edge not in self.edges:
                        self.edges.append(edge)
                        self.orc += O.G[u][v]['ricciCurvature']
        self.cms = None

class ClusterManager:
    def __init__(self, G, O):
        self.G = G
        self.O = O
        self.clusters = [Cluster(v, set([v]), G, O) for v in G.nodes()]
        self.next_id = G.number_of_nodes() + 1

    def orc_normalize(self):
        # Ricci curvature 값을 모두 모음
        ricci_values = [self.O.G[u][v]['ricciCurvature'] for u, v in self.O.G.edges()]
        # 최소값과 최대값 계산
        min_ricci = min(ricci_values)

        if min_ricci < 0:
            for u, v in self.G.edges():
                orc = self.O.G[u][v]['ricciCurvature']
                if orc < 0:
                    self.O.G[u][v]['ricciCurvature'] = orc / abs(min_ricci)

    def find_cluster_by_node(self, node):
        for cluster in self.clusters:
            if node in cluster.nodes:
                return cluster
        return None

    def merge_clusters(self, cluster1, cluster2):
        cc = [(min(u, v), max(u, v)) for u in cluster1.nodes for v in cluster2.nodes if self.G.has_edge(u, v)]
        t_orc = sum(self.O.G[u][v]['ricciCurvature'] for u, v in cc)
        cluster1.edges = cc + cluster1.edges + cluster2.edges
        cluster1.nodes = cluster1.nodes|cluster2.nodes
        cluster1.d = cluster1.d+cluster2.d
        cluster1.orc = cluster1.orc+cluster2.orc + t_orc
        self.clusters.remove(cluster2)

    @profile
    def calculate_cms(self, c, alpha, m):
        """ 전체 클러스터에 대한 CMS 값 계산 (ORCC와 NM 결합) """
        if isinstance(c, Cluster):
            l = len(c.edges)
            n = len(c.nodes)
            d = c.d
            orc = c.orc
        else:
            edges = [(min(u, v), max(u, v)) for u in c[0].nodes for v in c[1].nodes if self.G.has_edge(u, v)]
            t_orc = sum(self.O.G[u][v]['ricciCurvature'] for u, v in edges)
            l = len(edges + c[0].edges + c[0].edges)
            n = len(c[0].nodes | c[1].nodes)
            d = c[0].d + c[1].d
            orc = c[0].orc + c[1].orc + t_orc

        # orcc 계산
        if l == 0:
            orcc = 0
        else:
            orcc = orc/n

        # nm 계산
        nm = (l - (d ** 2 / (2 * m))) / (2 * m)

        return alpha * orcc + (1 - alpha) * nm

    def calculate_total_cms(self, alpha, m):
        sum = 0
        for cluster in self.clusters:
            sum += self.calculate_cms(cluster, alpha, m)
        return sum

@profile
def run(G, alpha, com):
    start_time = time.time()

    O = OllivierRicci(G, alpha=0.5, verbose="INFO")
    O.compute_ricci_curvature()
    C = ClusterManager(G, O)
    C.orc_normalize()
    m = G.number_of_edges()

    while len(C.clusters) > com:
        S = []
        connected_pairs = set() # 중복 방지
        for (u, v) in G.edges():
            c_u = C.find_cluster_by_node(u)
            c_v = C.find_cluster_by_node(v)

            if c_u.c_id != c_v.c_id:
                if ((c_u.c_id, c_v.c_id) not in connected_pairs and (c_v.c_id, c_u.c_id)) not in connected_pairs:
                    cuv = C.calculate_cms((c_v,c_u), alpha, m)
                    if c_u.cms is None:
                        cu = C.calculate_cms(c_u, alpha, m)
                    else: cu = c_u.cms
                    if c_v.cms is None:
                        cv = C.calculate_cms(c_v, alpha, m)
                    else: cv = c_v.cms
                    delta_cms = cuv - cu - cv
                    S.append((delta_cms, c_v, c_u))
                    connected_pairs.add((c_u.c_id, c_v.c_id))
        if len(S) == 0: continue
        ccms, c_p, c_q = max(S, key=lambda x: x[0])
        C.merge_clusters(c_p, c_q)

    end_time = time.time()
    communities = [c.nodes for c in C.clusters]

    return communities, end_time-start_time
