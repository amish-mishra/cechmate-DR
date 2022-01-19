import itertools
import numpy as np
import time
from scipy.spatial import Delaunay
import warnings


from .base import BaseFiltration

__all__ = ["DR"]


class DR(BaseFiltration):
    """ Construct a Delaunay-Rips filtration from the given data.

    Note
    =====

    Examples
    ========

        >>> r = DR()
        >>> simplices = r.build(X)
        >>> diagrams = r.diagrams(simplices)

    """
    def build(self, X):
        """
        Do the Delaunay-Rips filtration of a Euclidean point set (requires scipy)
        
        Parameters
        ===========
        X: Nxd array
            Array of N Euclidean vectors in d dimensions
        Returns
        ==========
        
        simplices: 
            Delaunay-Rips filtration for the data X
        """

        if X.shape[0] < X.shape[1]:
            warnings.warn(
                "The input point cloud has more columns than rows; "
                + "did you mean to transpose?"
            )
        maxdim = self.maxdim
        if not self.maxdim:
            maxdim = X.shape[1] - 1
        if maxdim > X.shape[1] - 1:
            warnings.warn(
                "maxdim exceeds computable homology dimension for input data using Delaunay-Rips; "
                + "setting maxdim to maximum computable homology dimension for input data."
            )
            maxdim = X.shape[1] - 1

        delaunay_faces = Delaunay(X).simplices   # Compute Delaunay Triangulation
        filtration = {} # track the simplices and their weights to avoid adding duplicates to filtration
        
        # Add 1-simplices, 2-simplices,... to the filtration in that order
        for simplex in delaunay_faces:
            simplex = sorted(simplex)
            for dim in range(2, maxdim+3):
                faces = self._find_subsets(simplex, dim)
                for face in faces:
                    if face not in filtration and dim == 2:
                        # assumption: Delaunay triangulation labeled vertices in the same order the data was inputted
                        d = self._euclidean(X[face[0]], X[face[1]])
                        filtration[face] = d
                    elif face not in filtration and dim > 2:   # simplex needs the weight of the max co-face
                        sub_faces = self._find_subsets(face, dim-1)
                        max_weight = -1.0
                        for sub_face in sub_faces:
                            weight = filtration[sub_face]
                            if weight > max_weight:
                                max_weight = weight
                        filtration[face] = max_weight

        simplices = [([i], 0) for i in range(X.shape[0])]
        simplices.extend(filtration.items())

        self.simplices_ = simplices
        return simplices

    def _euclidean(self, x, y):
        """
        Compute the euclidean distance between two points
        
        Parameters
        ----------
        x : ndarray
        y : ndarray
        
        Returns
        -------
        Distance between two input points : scalar
        """
        return np.sqrt(np.sum((x - y) ** 2))


    def _find_subsets(self, s, n):
        """
        Find all subsets of a given array-like object 
        
        Parameters
        ----------
        s : array-like
        n : size of desired subset
        
        Returns
        -------
        List of all subsets of the input array-like object
        """
        return list(itertools.combinations(s, n))


