import json
import os
from pprint import pprint

import numpy as np
import pandas as pd

from scipy.spatial.distance import pdist, squareform
from sklearn import datasets
from fastcluster import linkage

import matplotlib.pyplot as plt

import matplotlib.pyplot as plt

from common_function import read_json, calculate_ratio


def seriation(Z, N, cur_index):
    """Returns the order implied by a hierarchical tree (dendrogram).

       :param Z: A hierarchical tree (dendrogram).
       :param N: The number of points given to the clustering process.
       :param cur_index: The position in the tree for the recursive traversal.

       :return: The order implied by the hierarchical tree Z.
    """
    if cur_index < N:
        return [cur_index]
    else:
        left = int(Z[cur_index - N, 0])
        right = int(Z[cur_index - N, 1])
        return seriation(Z, N, left) + seriation(Z, N, right)


def compute_serial_matrix(dist_mat, method="ward"):
    """Returns a sorted distance matrix.

       :param dist_mat: A distance matrix.
       :param method: A string in ["ward", "single", "average", "complete"].

        output:
            - seriated_dist is the input dist_mat,
              but with re-ordered rows and columns
              according to the seriation, i.e. the
              order implied by the hierarchical tree
            - res_order is the order implied by
              the hierarhical tree
            - res_linkage is the hierarhical tree (dendrogram)

        compute_serial_matrix transforms a distance matrix into
        a sorted distance matrix according to the order implied
        by the hierarchical tree (dendrogram)
    """
    N = len(dist_mat)
    flat_dist_mat = squareform(dist_mat)
    res_linkage = linkage(flat_dist_mat, method=method)
    res_order = seriation(res_linkage, N, N + N - 2)
    seriated_dist = np.zeros((N, N))
    a, b = np.triu_indices(N, k=1)
    seriated_dist[a, b] = dist_mat[[res_order[i] for i in a], [res_order[j] for j in b]]
    seriated_dist[b, a] = seriated_dist[a, b]

    return seriated_dist, res_order, res_linkage


with open('../assets/ingredient_to_mol.json', 'r') as json_file:
    id_to_molecules = json.load(json_file)
data = []
i = -1
for ing_id_base in id_to_molecules:
    i += 1
    if i % 50 == 0:
        print("ing_id_base: " + ing_id_base)
    mol_ing_base = id_to_molecules[ing_id_base]
    line = {}
    for ing_id_2 in id_to_molecules:
        mol_ing = id_to_molecules[ing_id_2]
        ratio = round(calculate_ratio(mol_ing_base, mol_ing), 3)
        line[ing_id_2] = ratio
    data.append(line.copy())

df = pd.DataFrame(data, index=list(id_to_molecules.keys()))


#
# dist_mat = pd.read_csv("csv_files/pair_matrix.csv", delimiter='\t')
#
# print(dist_mat.shape[0])
# # N = len(iris.data)

distances = np.sqrt((1 - df) / 2)

ordered_dist_mat, res_order, res_linkage = compute_serial_matrix(distances.values, method='single')
plt.pcolormesh(distances)
plt.colorbar()
plt.title('Original order distance matrix')
plt.show()

plt.pcolormesh(ordered_dist_mat)
plt.colorbar()
plt.title('Re-ordered distance matrix')
plt.show()


def compute_HRP_weights(covariances, res_order):
    weights = pd.Series(1, index=res_order)
    clustered_alphas = [res_order]

    while len(clustered_alphas) > 0:
        clustered_alphas = [cluster[start:end] for cluster in clustered_alphas
                            for start, end in ((0, len(cluster) // 2),
                                               (len(cluster) // 2, len(cluster)))
                            if len(cluster) > 1]
        for subcluster in range(0, len(clustered_alphas), 2):
            left_cluster = clustered_alphas[subcluster]
            right_cluster = clustered_alphas[subcluster + 1]

            left_subcovar = covariances[left_cluster].loc[left_cluster]
            inv_diag = 1 / np.diag(left_subcovar.values)
            parity_w = inv_diag * (1 / np.sum(inv_diag))
            left_cluster_var = np.dot(parity_w, np.dot(left_subcovar, parity_w))

            right_subcovar = covariances[right_cluster].loc[right_cluster]
            inv_diag = 1 / np.diag(right_subcovar.values)
            parity_w = inv_diag * (1 / np.sum(inv_diag))
            right_cluster_var = np.dot(parity_w, np.dot(right_subcovar, parity_w))

            alloc_factor = 1 - left_cluster_var / (left_cluster_var + right_cluster_var)

            weights[left_cluster] *= alloc_factor
            weights[right_cluster] *= 1 - alloc_factor

    return weights


def compute_MV_weights(covariances):
    inv_covar = np.linalg.inv(covariances)
    u = np.ones(len(covariances))

    return np.dot(inv_covar, u) / np.dot(u, np.dot(inv_covar, u))


def compute_RP_weights(covariances):
    weights = (1 / np.diag(covariances))

    return weights / sum(weights)


def compute_unif_weights(covariances):
    return [1 / len(covariances) for i in range(len(covariances))]