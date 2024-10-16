import argparse
import networkx as nx
import csv
# import matplotlib.pyplot as plt

import CMS
import CD_ORC
import evaluate

argparse = argparse.ArgumentParser()

argparse.add_argument("--dataset", type=str, default="../dataset/karate")
argparse.add_argument("--algor", type=str, default="CMS")
argparse.add_argument("--alpha", type=float, default=0.1)
argparse.add_argument("--com", type=int, default=2)
args = argparse.parse_args()

file_path = args.dataset
G = nx.read_edgelist(file_path+"/network.dat", nodetype=int)
#self loop 제거
G.remove_edges_from(nx.selfloop_edges(G))
#calculate average degree
total_degree = sum(dict(G.degree()).values())
average_degree = total_degree / G.number_of_nodes()
# print(G.number_of_nodes(), G.number_of_edges(),average_degree)

# for i in range(11):
#     alpha = round(i * 0.1, 1)
alpha = args.alpha
if args.algor == "CMS":
    communities, orc_time, time, merge = CMS.run(G, alpha, args.com)
elif args.algor == "ORC":
    communities, time = CD_ORC.run(G)

node2community = {}
for i, community in enumerate(communities):
    for node in community:
        node2community[node] = i
score = evaluate.run(G, file_path+"/community.dat", node2community)
# print(f'Time:{time}, NMI:{nmi}, ARI:{ari}, F1_score:{f1}, #com:{len(communities)}')

# # 커뮤니티에 따른 노드 색상을 설정
# unique_communities = set(node2community.values())  # 커뮤니티의 유니크한 값들
# color_map = plt.cm.get_cmap('rainbow', len(unique_communities))  # 커뮤니티별 색상 생성
# community_colors = {community: color_map(i) for i, community in enumerate(unique_communities)}
#
# # 각 노드에 커뮤니티 색상을 부여
# node_colors = [community_colors[node2community[node]] for node in G.nodes()]
#
# # 그래프 시각화
# plt.figure(figsize=(10, 8))
# pos = nx.spring_layout(G, seed=42)  # 레이아웃 결정
#
# # 노드와 엣지를 그리기 (노드 색상은 커뮤니티별로 다르게)
# nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color='gray',
#         node_size=500, font_size=10, font_color='black')
#
# plt.show()

data_name = file_path.split('/')[2]
if data_name == 'syn_dataset':
    data_name = file_path.split('/')[4]
with open(file_path+f"/output/{args.algor}_a{alpha}.txt", "w") as f:
    f.write(f"Time:{time}\n")
    # f.write(f'ORC_Time:{orc_time}\n')
    for k, v in score.items():
        f.write(f"{k}:{v}\n")
    f.write(f"#com:{len(communities)}\n")
    # write node2community sorted by node_id
    for node in sorted(node2community.keys()):
        f.write(f"{node} {node2community[node]}\n")
csv_name = '../output/real_server.csv'
if args.algor != 'CMS':
    with open(csv_name, 'a', newline='') as f:
        # writer = csv.DictWriter(f, fieldnames=['data', 'algorithm', 'time', 'alpha']+list(score.keys())+['#com',  'merge', 'merge_avg', 'merge_sum', 'merge_sum_avg'])
        writer = csv.DictWriter(f, fieldnames=['data', 'algorithm', 'time']+list(score.keys())+['#com'])
        writer.writerow({
            'data':data_name,
            'algorithm':args.algor,
            'time':time}
            |score|
            {'#com':len(communities)})
else:
    with open(csv_name, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['data', 'algorithm', 'time', 'alpha']+list(score.keys())+['#com',  'merge', 'merge_avg'])
        # writer = csv.DictWriter(f, fieldnames=['data', 'algorithm', 'time']+list(score.keys())+['#com'])
        writer.writerow({
            'data':data_name,
            'algorithm':args.algor,
            'time':time,
            'alpha': alpha
                        }
            |score|
            {'#com':len(communities),
             'merge': merge,
             'merge_avg': sum(merge)/len(merge)
        })