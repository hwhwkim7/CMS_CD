from sklearn.metrics import normalized_mutual_info_score, adjusted_rand_score, f1_score
from cdlib import evaluation
from cdlib import NodeClustering
from cdlib.classes import AttrNodeClustering
import networkx as nx

# Reading the Ground-Truth Community Data
def load_ground_truth(file_path):
    node_to_community = {}
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                node, community = int(parts[0]), int(parts[1])
                node_to_community[node] = community
    return node_to_community

def convert_labels_to_communities(labels):
    communities = {}
    for node, community in enumerate(labels):
        if community not in communities:
            communities[community] = []
        communities[community].append(node+1)
    return list(communities.values())

# Calculating NMI Score
def calculate(G, true_communities, detected_communities):
    # Ensure the labels are in the same order for both true and detected
    nodes = sorted(set(true_communities) | set(detected_communities))
    detected_communities = dict(sorted(detected_communities.items()))

    true_labels_vector = [true_communities[node] for node in nodes]
    detected_labels_vector = [detected_communities.get(node, -1) for node in nodes]

    true_labels = convert_labels_to_communities(true_labels_vector)
    detected_labels = convert_labels_to_communities(detected_labels_vector)

    communities2node = {}
    for n, c in true_communities.items():
        if c not in communities2node:
            communities2node[c] = [n]
        else:
            communities2node[c].append(n)
    # print(communities2node)

    gt_communities = NodeClustering(communities=true_labels, graph=G)
    dt_communities = NodeClustering(communities=detected_labels, graph=G)

    att_dt_communities = AttrNodeClustering(communities=detected_labels, graph=G, coms_labels=communities2node)

    scores = {
        'nmi':normalized_mutual_info_score(true_labels_vector, detected_labels_vector),
        'ari':adjusted_rand_score(true_labels_vector, detected_labels_vector),
        # 'f1_score':f1_score(true_labels_vector, detected_labels_vector, average='macro'),
        # "adjusted_rand_index": evaluation.adjusted_rand_index(gt_communities, dt_communities).score,
        # "variation_of_information": evaluation.variation_of_information(gt_communities, dt_communities).score,
        # "average_internal_degree": evaluation.average_internal_degree(G, dt_communities).score,
        # "conductance": evaluation.conductance(G, dt_communities).score,
        # "cut_ratio": evaluation.cut_ratio(G, dt_communities).score,
        # "expansion": evaluation.expansion(G, dt_communities).score,
        # "internal_edge_density": evaluation.internal_edge_density(G, dt_communities).score,
        # "modularity": evaluation.newman_girvan_modularity(G, dt_communities).score,
        # "triangle_participation_ratio": evaluation.triangle_participation_ratio(G, dt_communities).score,
        # "avg_distance": evaluation.avg_distance(G, dt_communities).score,
        # "avg_embeddedness": evaluation.avg_embeddedness(G, dt_communities).score,
        # "edges_inside": evaluation.edges_inside(G, dt_communities).score,
        # "fraction_over_median_degree": evaluation.fraction_over_median_degree(G, dt_communities).score,
        # "hub_dominance": evaluation.hub_dominance(G, dt_communities).score,
        # "normalized_cut": evaluation.normalized_cut(G, dt_communities).score,
        # "max_odf": evaluation.max_odf(G, dt_communities).score,
        # "avg_odf": evaluation.avg_odf(G, dt_communities).score,
        # "flake_odf": evaluation.flake_odf(G, dt_communities).score,
        # "scaled_density": evaluation.scaled_density(G, dt_communities).score,
        # "significance": evaluation.significance(G, dt_communities).score,
        # "size": evaluation.size(G, dt_communities).score,
        # "surprise": evaluation.surprise(G, dt_communities).score,
        # "erdos_renyi_modularity": evaluation.erdos_renyi_modularity(G, dt_communities).score,
        # "link_modularity": evaluation.link_modularity(G, dt_communities).score,
        # "modularity_density": evaluation.modularity_density(G, dt_communities).score,
        # "modularity_overlap": evaluation.modularity_overlap(G, dt_communities).score,
        # "newman_girvan_modularity": evaluation.newman_girvan_modularity(G, dt_communities).score,
        # "z_modularity": evaluation.z_modularity(G, dt_communities).score,
        # # "purity": evaluation.purity(att_dt_communities).score,
        # "adjusted_mutual_information": evaluation.adjusted_mutual_information(gt_communities, dt_communities).score,
        # # "mi": evaluation.mi(gt_communities, dt_communities).score,
        # "rmi": evaluation.rmi(gt_communities, dt_communities).score,
        # "normalized_mutual_information": evaluation.normalized_mutual_information(gt_communities, dt_communities).score,
        # "overlapping_normalized_mutual_information_LFK": evaluation.overlapping_normalized_mutual_information_LFK(gt_communities, dt_communities).score,
        # "overlapping_normalized_mutual_information_MGH": evaluation.overlapping_normalized_mutual_information_MGH(gt_communities, dt_communities).score,
        # "rand_index": evaluation.rand_index(gt_communities, dt_communities).score,
        # "omega": evaluation.omega(gt_communities, dt_communities).score,
        "nf1": evaluation.nf1(gt_communities, dt_communities).score,
        # "southwood_index": evaluation.southwood_index(gt_communities, dt_communities).score,
        # "rogers_tanimoto_index": evaluation.rogers_tanimoto_index(gt_communities, dt_communities).score,
        # "sorensen_index": evaluation.sorensen_index(gt_communities, dt_communities).score,
        # "dice_index": evaluation.dice_index(gt_communities, dt_communities).score,
        # "czekanowski_index": evaluation.czekanowski_index(gt_communities, dt_communities).score,
        # "fowlkes_mallows_index": evaluation.fowlkes_mallows_index(gt_communities, dt_communities).score,
        # "jaccard_index": evaluation.jaccard_index(gt_communities, dt_communities).score,
        # "sample_expected_sim": evaluation.sample_expected_sim(gt_communities, dt_communities).score,
        # "overlap_quality": evaluation.overlap_quality(gt_communities, dt_communities).score,
        # "geometric_accuracy": evaluation.geometric_accuracy(gt_communities, dt_communities).score,
        # "classification_error": evaluation.classification_error(gt_communities, dt_communities).score,
        # "ecs": evaluation.ecs(gt_communities, dt_communities).score,
    }
    return scores


def run(G, ground_truth_file, node2community):
    ground_truth = load_ground_truth(ground_truth_file)
    # print(node2community)

    score = calculate(G, ground_truth, node2community)
    return score