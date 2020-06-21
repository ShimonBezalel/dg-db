from pprint import pprint

import pandas as pd
import numpy as np
from scipy.linalg import block_diag
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import squareform
import matplotlib.pyplot as plt

nb_alphas = 250
nb_observations = int(0.3 * 252)

# build a hierarchical block diagonal correlation matrix
quality = 0.6 * np.ones((nb_alphas // 6, nb_alphas // 6))
value = 2.4 * np.ones((nb_alphas // 2, nb_alphas // 2))
momentum = 2.6 * np.ones((int(nb_alphas * (1 - 1 / 6 - 1 / 2) + 1),
                          int(nb_alphas * (1 - 1 / 6 - 1 / 2) + 1)))

correl_mom_value = -1.2 * np.ones((int(nb_alphas * (1 - 1 / 6)) + 1,
                                   int(nb_alphas * (1 - 1 / 6)) + 1))

correl = (block_diag(quality, correl_mom_value) +
          block_diag(quality, momentum, value)) / 3
np.fill_diagonal(correl, 1)

mean_returns = np.zeros(nb_alphas)
volatilities = ([np.sqrt(0.1 / np.sqrt(252))] * (nb_alphas // 3) +
                [np.sqrt(0.3 / np.sqrt(252))] * (nb_alphas - nb_alphas // 3 - nb_alphas // 6) +
                [np.sqrt(0.5 / np.sqrt(252))] * (nb_alphas // 6))
covar = np.multiply(correl,
                    np.outer(np.array(volatilities),
                             np.array(volatilities)))

covar = pd.read_csv("assets\csv_files\statistical_aroma_matrix.csv", sep='\t')

covar = pd.DataFrame(covar)

pprint(correl)

# plt.pcolormesh(correl)
# plt.colorbar()
# plt.title('Correlation matrix')
# plt.show()

# plt.pcolormesh(covar)
# plt.colorbar()
# plt.title('Covariance matrix')
# plt.show()

alphas_returns = np.random.multivariate_normal(
    mean_returns, cov=covar, size=nb_observations)

alphas_returns = pd.DataFrame(alphas_returns)
plt.figure(figsize=(20, 10))
# plt.plot(alphas_returns.cumsum())
# plt.title('Performance of the different alphas', fontsize=24)
# plt.show()
#
#
estimate_correl = alphas_returns.corr(method='pearson')
estimate_covar = alphas_returns.cov()
# plt.pcolormesh(estimate_correl)
# plt.colorbar()
# plt.title('Estimated correlation matrix')
# plt.show()

# plt.pcolormesh(estimate_covar)
# plt.colorbar()
# plt.title('Estimated covariance matrix')
# plt.show()
#
distances = np.sqrt((1 - estimate_correl) / 2)
pprint(distances)


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
        return (seriation(Z, N, left) + seriation(Z, N, right))


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


ordered_dist_mat, res_order, res_linkage = compute_serial_matrix(distances.values, method='single')

plt.pcolormesh(distances)
plt.colorbar()
plt.title('Original order distance matrix')
plt.show()

plt.pcolormesh(ordered_dist_mat)
plt.colorbar()
plt.title('Re-ordered distance matrix')
plt.show()
