from sklearn.metrics import normalized_mutual_info_score, adjusted_rand_score


def run(ground_truth_file, node2community):
    ground_truth = {}

    # Ground truth 파일 읽기
    with open(ground_truth_file, 'r') as f:
        for line in f:
            node, community = map(int, line.strip().split())
            ground_truth[node] = community

    # node2community와 ground truth를 사용하여 리스트로 변환
    y_true = []
    y_pred = []

    for node in sorted(ground_truth.keys()):
        y_true.append(ground_truth[node])  # Ground truth 커뮤니티
        y_pred.append(node2community.get(node, -1))  # Predicted 커뮤니티, 없으면 -1로 처리

    # NMI와 ARI 계산
    nmi = normalized_mutual_info_score(y_true, y_pred)
    ari = adjusted_rand_score(y_true, y_pred)

    return nmi, ari