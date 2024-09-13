import copy
import numpy as np
import networkx as nx
import time
from GraphRicciCurvature.OllivierRicci import OllivierRicci

class Cluster:
    def __init__(self, cluster_id, nodes, G):
        self.c_id = cluster_id
        self.nodes = set(nodes)
        self.edges = []
        for u in self.nodes:
            for v in self.nodes-{u}:
                if G.has_edge(u,v):
                    edge = (min(u,v), max(u,v))
                    if edge not in self.edges:
                        self.edges.append(edge)

    def contains_node(self, node):
        return node in self.nodes

    @profile
    def calculate_orcc(self, O):
        """ ORCC 값을 계산 (Ollivier-Ricci Curvature Contribution) """
        # 클러스터 내부의 엣지들에 대해 ORCC를 계산
        if len(self.edges) == 0:
            return 0  # 엣지가 없을 경우 0 반환
        orc_sum = 0
        for u, v in self.edges:
            orc_sum += O.G[u][v]['ricciCurvature']
        return orc_sum / len(self.edges)  # ORC 평균 계산

    @profile
    def calculate_modularity(self, G, m):
        l = len(self.edges)
        d = 0
        for u in self.nodes:
            d += G.degree(u)
        return ( l - (d**2/(2*m)) ) / (2*m)

class ClusterManager:
    def __init__(self, G, O):
        self.G = G
        self.O = O
        self.clusters = [Cluster(v, set([v]), G) for v in G.nodes()]
        self.next_id = G.number_of_nodes() + 1

    def num_clusters(self):
        return len(self.clusters)

    @profile
    def add_cluster(self, nodes):
        cluster = Cluster(self.next_id, nodes, self.G)
        self.clusters.append(cluster)
        self.next_id += 1
        return cluster

    def find_cluster_by_node(self, node):
        for cluster in self.clusters:
            if cluster.contains_node(node):
                return cluster
        return None

    def merge_clusters(self, cluster1, cluster2):
        cc = [(min(u, v), max(u, v)) for u in cluster1.nodes for v in cluster2.nodes if self.G.has_edge(u, v)]
        cluster1.edges = cc + cluster1.edges + cluster2.edges
        cluster1.nodes = cluster1.nodes|cluster2.nodes
        self.clusters.remove(cluster2)

    @profile
    def calculate_cms(self, cc, alpha, m):
        """ 전체 클러스터에 대한 CMS 값 계산 (ORCC와 NM 결합) """
        if isinstance(cc, Cluster):
            c = cc
            remove = False
        else:
            c = self.add_cluster(cc)
            remove = True
        orcc = c.calculate_orcc(self.O)  # 각 클러스터의 ORCC 합산
        nm = c.calculate_modularity(self.G, m)  # 전체 클러스터링의 모듈러리티 계산
        if remove: self.clusters.remove(c)
        return alpha * orcc + (1 - alpha) * nm

    def calculate_total_cms(self, alpha, m):
        sum = 0
        for cluster in self.clusters:
            sum += self.calculate_cms(cluster, alpha, m)
        return sum

@profile
def run(G, alpha):
    start_time = time.time()

    O = OllivierRicci(G, alpha=0.5, verbose="INFO")
    O.compute_ricci_curvature()
    C = ClusterManager(G, O)
    m = G.number_of_edges()

    CMS_max = -np.inf
    C_best = None

    while C.num_clusters() > 1:
        S = []
        connected_pairs = set() # 중복 방지
        for (u, v) in G.edges():
            c_u = C.find_cluster_by_node(u)
            c_v = C.find_cluster_by_node(v)

            if c_u.c_id != c_v.c_id:
                if ((c_u.c_id, c_v.c_id) not in connected_pairs and (c_v.c_id, c_u.c_id)) not in connected_pairs:
                    delta_cms = C.calculate_cms(c_v.nodes|c_u.nodes, alpha, m)
                    S.append((delta_cms, c_v, c_u))
                    connected_pairs.add((c_u.c_id, c_v.c_id))
        if len(S) == 0: continue
        ccms, c_p, c_q = max(S, key=lambda x: x[0])
        # print('====================================')
        # print(f'merge cluster:: CMS:{ccms}, c1:{len(c_p.nodes)}, c2:{len(c_q.nodes)}')
        C.merge_clusters(c_p, c_q)
        CMS_current = C.calculate_total_cms(alpha, m)
        # print('CMS 값 비교')
        # print(f'current:{CMS_current}, max:{CMS_max}')
        if CMS_current > CMS_max:
            CMS_max = CMS_current
            C_best = copy.deepcopy(C)

    end_time = time.time()
    communities = [c.nodes for c in C_best.clusters]

    # for i, community in enumerate(communities, 1):
    #     print(f"Community {i}: {community}")

    return communities, end_time-start_time
