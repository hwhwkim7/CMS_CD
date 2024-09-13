import argparse
import networkx as nx
import copy
import csv

import CMS
import CD_ORC
import evaluate

argparse = argparse.ArgumentParser()

argparse.add_argument("--dataset", type=str, default="../dataset/railway")
argparse.add_argument("--algor", type=str, default="CMS")
argparse.add_argument("--alpha", type=float, default=0.5)
args = argparse.parse_args()

file_path = args.dataset
G = nx.read_edgelist(file_path+"/network.dat", nodetype=int)
#self loop 제거
G.remove_edges_from(nx.selfloop_edges(G))
#calculate average degree
total_degree = sum(dict(G.degree()).values())
average_degree = total_degree / G.number_of_nodes()
print(G.number_of_nodes(), G.number_of_edges(),average_degree)

coms = list(nx.connected_components(G))
Gs = [G.subgraph(nodes).copy() for nodes in coms]

if args.algor == "CMS":
    time = 0
    communities = []
    for G_ in Gs:
        c, t = CMS.run(G_, args.alpha)
        communities.extend(c)
        time += t
elif args.algor == "ORC":
    communities, time = CD_ORC.run(G)

node2community = {}
for i, community in enumerate(communities):
    for node in community:
        node2community[node] = i
nmi, ari = evaluate.run(file_path+"/community.dat", node2community)
print(f'Time:{time}, NMI:{nmi}, ARI:{ari}, #com:{len(communities)}')
data_name = file_path.split('/')[2]
with open(file_path+f"/output/{args.algor}_a{args.alpha}.txt", "w") as f:
    f.write(f"Time:{time}\n")
    f.write(f"NMI:{nmi}\n")
    f.write(f"ARI:{ari}\n")
    f.write(f"#com:{len(communities)}")
    # write node2community sorted by node_id
    for node in sorted(node2community.keys()):
        f.write(f"{node} {node2community[node]}\n")

with open('../output/result.csv', 'a', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['data', 'algorithm', 'time', 'alpha', 'nmi', 'ari', '#com'])
    writer.writerow({
        'data':data_name,
        'algorithm':args.algor,
        'time':time,
        'alpha': args.alpha,
        'nmi':nmi,
        'ari':ari,
        '#com':len(communities)
    })