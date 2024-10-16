from networkx.algorithms.community import girvan_newman
import community as community_louvain
from networkx.algorithms.community import label_propagation_communities
import networkx as nx
from sklearn.cluster import KMeans, DBSCAN
import numpy as np
import argparse
import csv
import time

import CMS
import CD_ORC
import evaluate

# CMS
def cms(G, com):
    communities, _, t, _, _ = CMS.run(G, 0.1, com)
    node2community = {}
    for i, community in enumerate(communities):
        for node in community:
            node2community[node] = i+1
    return node2community, t, len(communities)

# ORC
def orc(G):
    communities, t = CD_ORC.run(G)
    node2community = {}
    for i, community in enumerate(communities):
        for node in community:
            node2community[node] = i+1
    return node2community, t, len(communities)

# Girvan-Newman Algorithm
def nm(G):
    st = time.time()
    communities = next(girvan_newman(G))  # 첫 번째 레벨의 커뮤니티만 사용
    t = time.time() - st
    node2community = {}
    for i, community in enumerate(communities):
        for node in community:
            node2community[node] = i+1
    return node2community, t, len(communities)

# Label Propagation
def label(G):
    st = time.time()
    communities = label_propagation_communities(G)
    t = time.time() - st
    node2community = {}
    for i, community in enumerate(communities):
        for node in community:
            node2community[node] = i+1
    return node2community, t, len(communities)
# Louvain
def louvain(G):
    st = time.time()
    partition = community_louvain.best_partition(G)
    t = time.time() - st
    return partition, t, len(set(partition.values()))

# Asynchronous Fluid Communities
def fluid_community_detection(G, k):
    st = time.time()
    communities = nx.community.asyn_fluidc(G, k)
    t = time.time() - st
    node_to_community = {}
    for i, comm in enumerate(communities):
        for node in comm:
            node_to_community[node] = i+1
    return node_to_community, t, len(communities)

# K-means Clustering
def kmeans_clustering(data, k):
    st = time.time()
    # data는 노드에 대한 특성/좌표 데이터 (2차원 배열)
    kmeans = KMeans(n_clusters=k)
    labels = kmeans.fit_predict(data)
    t = time.time() - st

    # 클러스터 결과를 dict 형식으로 변환
    node_to_community = {idx: label for idx, label in enumerate(labels)}
    return node_to_community, t, len(labels)

argparse = argparse.ArgumentParser()
argparse.add_argument("--dataset", type=str, default="../dataset/karate")
argparse.add_argument("--com", type=int, default=2)
args = argparse.parse_args()

file_path = args.dataset
G = nx.read_edgelist(file_path+"/network.dat", nodetype=int)
#self loop 제거
G.remove_edges_from(nx.selfloop_edges(G))
#calculate average degree
total_degree = sum(dict(G.degree()).values())
average_degree = total_degree / G.number_of_nodes()

row = []
data_name = file_path.split("/")[2]

# print('CMS')
# cms_cd, t, len_c = cms(G, args.com)
# score = evaluate.run(G, file_path+'/community.dat', cms_cd)
# row.append({'data':data_name, 'algorithm':'cms_cd', 'time':t} | score | {'#com':len_c})

# print('ORC')
# orc_cd, t, len_c = orc(G)
# score = evaluate.run(G, file_path+'/community.dat', orc_cd)
# row.append({'data':data_name, 'algorithm':'orc_cd', 'time':t} | score | {'#com':len_c})

print('NM')
nm_cd, t, len_c = nm(G)
score = evaluate.run(G, file_path+'/community.dat', nm_cd)
row.append({'data':data_name, 'algorithm':'nm_cd', 'time':t} | score | {'#com':len_c})

print('LABEL')
label_cd, t, len_c = label(G)
score = evaluate.run(G, file_path+'/community.dat', label_cd)
row.append({'data':data_name, 'algorithm':'label_cd', 'time':t} | score | {'#com':len_c})

print('LOUVAIN')
louvain_cd, t, len_c = louvain(G)
score = evaluate.run(G, file_path+'/community.dat', louvain_cd)
row.append({'data':data_name, 'algorithm':'louvain_cd', 'time':t} | score | {'#com':len_c})

# f_cd, t = fluid_community_detection(G, args.com)
# score = evaluate.run(G, file_path+'/community.dat', orc_cd)
# row.append([data_name, 'orc_cd', t] + score + [len(orc_cd)])

# kmeans_cd, t = kmeans_clustering(G, args.com)
# score = evaluate.run(G, file_path+'/community.dat', kmeans_cd)
# row.append([data_name, 'kmeans_cd', t] + score + [len(kmeans_cd)])

data_name = file_path.split('/')[2]
with open('../output/compare_scale.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    for r in row:
        writer.writerow(r.values())

# print(score.keys())


# score = evaluate.run(G, file_path+"/community.dat", node2community)
# print(f'Time:{time}, NMI:{nmi}, ARI:{ari}, #com:{len(communities)}')

