import time
from GraphRicciCurvature.OllivierRicci import OllivierRicci
import itertools
import queue
from sortedcontainers import SortedDict


class PriorityQueue:
    def __init__(self):
        self.data = SortedDict()
        self.node_to_priority = {}  # 노드를 키로, 해당 노드의 우선순위를 값으로 하는 dict

    # @profile
    def push(self, node, priority):
        # 우선순위를 키로 사용하여 노드를 추가
        if priority not in self.data:
            self.data[priority] = set()
        self.data[priority].add(node)
        self.node_to_priority[node] = priority
        # self.show()

    # @profile
    def pop(self):
        # 가장 높은 우선순위의 노드를 반환하고 제거
        if not self.data:
            raise IndexError("pop from empty priority queue")
        highest_priority = self.data.peekitem(-1)[0]  # tuple 반환하니까 그 앞에 key
        node = self.data[highest_priority].pop()
        del self.node_to_priority[node]
        if not self.data[highest_priority]:
            del self.data[highest_priority]
        return node

    # @profile
    def remove(self, node):
        # 특정 노드의 우선순위를 찾아서 노드를 제거 contain을 확인 한 후에 사용함.
        priority = self.node_to_priority[node]
        nodes = self.data[priority]
        nodes.remove(node)
        if not nodes:
            del self.data[priority]
        del self.node_to_priority[node]

    # @profile
    def empty(self):
        # 큐가 비어있는지 확인
        return len(self.data) == 0

    # @profile
    def contains(self, node):
        # 특정 노드가 큐에 있는지 확인
        return node in self.node_to_priority


class Cluster:
    def __init__(self, cluster_id, node, G, alpha):
        self.c_id = cluster_id
        self.nodes = set(node)
        self.edge = 0  # number of edges
        self.d = G.degree[node[0]]  # degree sum
        self.orc = 0  # orc sum
        self.cms = None
        self.merge = 0


class ClusterManager:
    def __init__(self, G, O):
        self.G = G
        self.O = O
        self.clusters = {v: Cluster(v, [v], G, O) for v in list(G.nodes())}
        self.next_id = G.number_of_nodes() + 1
        self.c_edges = {}
        for (u, v) in G.edges():
            # edge, 클러스터 사이의 엣지 갯수, 클러스터 사이의 엣지 ORC
            self.c_edges[(min(u, v), max(u, v))] = [1, O.G[u][v]['ricciCurvature'], 0, None]
        self.PQ = PriorityQueue()

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
        # print(f'===== merge: {cluster1.c_id}, {cluster2.c_id} =====')
        # for c in self.c_edges.items():
        #     print(c)
        if cluster1.c_id == 24:
            print()
        num_edge, orc, torc, cms = self.c_edges[(cluster1.c_id, cluster2.c_id)]
        cluster1.edge = num_edge + cluster1.edge + cluster2.edge
        cluster1.nodes = cluster1.nodes | cluster2.nodes
        cluster1.d = cluster1.d + cluster2.d
        cluster1.orc = torc
        cluster1.cms = cms
        cluster1.merge = max(cluster1.merge, cluster2.merge) + 1

        del self.c_edges[(cluster1.c_id, cluster2.c_id)]
        # merge에 따라 연결이 바뀌는 클러스터 탐색
        change_key = {}
        remove_key = []
        for (cp_id, cq_id), [num_edge, sum_orc, _, _] in self.c_edges.items():
            if cluster2.c_id == cp_id:
                key = (min(cluster1.c_id, cq_id), max(cluster1.c_id, cq_id))
                remove_key.extend([(cp_id, cq_id)])
            elif cluster2.c_id == cq_id:
                key = (min(cluster1.c_id, cp_id), max(cluster1.c_id, cp_id))
                remove_key.extend([(cp_id, cq_id)])
            else:
                continue

            if key in self.c_edges:
                lst_o = self.c_edges[key]
                if key in change_key:
                    lst_c = change_key[key]
                    change_key[key] = [lst_c[0] + lst_o[0] + num_edge, lst_c[1] + lst_o[1] + sum_orc]
                else:
                    change_key[key] = [lst_o[0] + num_edge, lst_o[1] + sum_orc]
            else:
                if key in change_key:
                    lst_c = change_key[key]
                    change_key[key] = [lst_c[0] + num_edge, lst_c[1] + sum_orc]
                else:
                    change_key[key] = [num_edge, sum_orc]

        for c in remove_key:
            self.c_edges.pop(c)
            self.PQ.remove(c)
        del self.clusters[cluster2.c_id]

        # print('=== merge 이후 ===')
        # for c in self.c_edges.items():
        #     print(c)
        return change_key

    # @profile
    def calculate_cms(self, c, alpha, m, num_con=0, orc_sum=0):
        """ 전체 클러스터에 대한 CMS 값 계산 (ORCC와 NM 결합) """
        if isinstance(c, Cluster):
            l = c.edge
            n = len(c.nodes)
            d = c.d
            orc = c.orc
        else:
            l = c[0].edge + c[1].edge + num_con
            n = len(c[0].nodes | c[1].nodes)
            d = c[0].d + c[1].d
            orc = c[0].orc + c[1].orc + orc_sum

        # orcc 계산
        if l == 0:
            orcc = 0
        else:
            orcc = orc / n

        # nm 계산
        nm = (2 * l - (d ** 2 / (2 * m))) / (2 * m)

        return alpha * orcc + (1 - alpha) * nm, orc


# @profile
def run(G, alpha, com):
    start_time = time.time()
    orc_start = time.time()
    O = OllivierRicci(G, alpha=0.5, verbose="INFO")
    O.compute_ricci_curvature()
    C = ClusterManager(G, O)
    C.orc_normalize()
    orc_time = time.time() - orc_start
    m = G.number_of_edges()

    # initialise PQ
    for key, [num_edge, sum_orc, _, _] in C.c_edges.items():
        cu = C.clusters[key[0]]
        cv = C.clusters[key[1]]
        cuv_cms, torc = C.calculate_cms((cu, cv), alpha, m, num_edge, sum_orc)
        if cu.cms is None:
            cu.cms, _ = C.calculate_cms(cu, alpha, m)
        if cv.cms is None:
            cv.cms, _ = C.calculate_cms(cv, alpha, m)
        C.c_edges[key][2] = torc
        C.c_edges[key][3] = cuv_cms
        delta = cuv_cms - cu.cms - cv.cms
        C.PQ.push(key, delta)

    while len(C.clusters) > com and C.PQ:
        # delta가 가장 큰 connected Cluster pair return
        key = C.PQ.pop()
        change_key = C.merge_clusters(C.clusters[key[0]], C.clusters[key[1]])

        for k, [n_e, s_o] in change_key.items():

            cu = C.clusters[k[0]]
            cv = C.clusters[k[1]]
            cuv_cms, torc = C.calculate_cms((cu, cv), alpha, m, n_e, s_o)
            if cu.cms is None:
                cu.cms, _ = C.calculate_cms(cu, alpha, m)
            if cv.cms is None:
                cv.cms, _ = C.calculate_cms(cv, alpha, m)
            C.c_edges[k] = [n_e, s_o, torc, cuv_cms]
            delta = cuv_cms - cu.cms - cv.cms
            if C.PQ.contains(k):
                C.PQ.remove(k)
            C.PQ.push(k, delta)

    end_time = time.time()
    communities = [list(c.nodes) for c in C.clusters.values()]
    merge = [c.merge for c in C.clusters.values()]

    return communities, orc_time, end_time - start_time, merge
