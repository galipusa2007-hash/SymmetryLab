import numpy as np

class SymmetryValidator:
    @staticmethod
    def validate(molecule, transformed, tolerance=1e-5):
        original = molecule.get_coordinates()
        transformed = np.asarray(transformed, dtype=float)
        if transformed.shape != original.shape:
            return False

        # Bipartite matching, not a nearest-neighbor greedy choice.
        for element in set(molecule.atoms):
            indices = [i for i, symbol in enumerate(molecule.atoms) if symbol == element]
            source = original[indices]
            target = transformed[indices]
            compatible = (np.linalg.norm(target[:,None,:]-source[None,:,:],axis=2) <= tolerance)
            matches = [-1]*len(indices)

            def assign(i, visited):
                for j in range(len(indices)):
                    if compatible[i,j] and not visited[j]:
                        visited[j] = True
                        if matches[j] == -1 or assign(matches[j],visited):
                            matches[j] = i
                            return True
                return False

            for i in range(len(indices)):
                if not assign(i,[False]*len(indices)):
                    return False
        return True
