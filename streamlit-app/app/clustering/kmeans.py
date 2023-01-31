from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


class KMEANS:
    def k_means_cluster(
        self, no_of_clusters, input_df, x_coord_col_name, y_coord_col_name
    ):
        kmeans = KMeans(n_clusters=no_of_clusters).fit(
            input_df[[x_coord_col_name, y_coord_col_name]]
        )
        fig = plt.figure(figsize=(12, 12))
        plt.xlabel(x_coord_col_name)
        plt.ylabel(y_coord_col_name)
        plt.title(x_coord_col_name + " vs " + y_coord_col_name)
        plt.grid(True)
        plt.scatter(
            input_df[x_coord_col_name],
            input_df[y_coord_col_name],
            c=kmeans.labels_.astype(float),
            s=50,
            alpha=0.5,
        )
        centroids = kmeans.cluster_centers_
        return fig
        # print(centroids)
