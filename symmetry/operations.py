from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class SymmetryOperation:
    name: str
    matrix: np.ndarray
    kind: str = 'identity'
    axis: np.ndarray | None = None
    normal: np.ndarray | None = None
    angle: float = 0.0

class SymmetryOperations:
    @staticmethod
    def identity():
        return np.eye(3)

    @staticmethod
    def rotation(axis, angle_degrees):
        axis = np.asarray(axis, dtype=float)
        axis /= np.linalg.norm(axis)
        x,y,z = axis
        t = np.radians(angle_degrees)
        c,s = np.cos(t),np.sin(t)
        v = 1-c
        return np.array([
            [v*x*x+c, v*x*y-s*z, v*x*z+s*y],
            [v*x*y+s*z, v*y*y+c, v*y*z-s*x],
            [v*x*z-s*y, v*y*z+s*x, v*z*z+c],
        ])

    @staticmethod
    def reflection(normal):
        normal = np.asarray(normal, dtype=float)
        normal /= np.linalg.norm(normal)
        return np.eye(3)-2*np.outer(normal,normal)

    @staticmethod
    def inversion():
        return -np.eye(3)

    @staticmethod
    def improper_rotation(axis, angle_degrees):
        return SymmetryOperations.reflection(axis) @ SymmetryOperations.rotation(axis,angle_degrees)

    @staticmethod
    def apply(coordinates, matrix):
        return np.asarray(coordinates,dtype=float) @ np.asarray(matrix).T

    @staticmethod
    def get_operations(group):
        e = SymmetryOperations.identity()
        r = SymmetryOperations.rotation
        m = SymmetryOperations.reflection
        s = SymmetryOperations.improper_rotation
        x = np.array([1.,0.,0.])
        y = np.array([0.,1.,0.])
        z = np.array([0.,0.,1.])

        def op(name, matrix, kind='identity', axis=None, normal=None, angle=0):
            return SymmetryOperation(name,matrix,kind,axis,normal,angle)

        if group == 'C2v':
            return [
                op('E',e),
                op('C₂(z)',r(z,180),'rotation',axis=z,angle=180),
                op('σᵥ(xz)',m(y),'reflection',normal=y),
                op('σᵥ(yz)',m(x),'reflection',normal=x),
            ]
        if group == 'D3h':
            ops = [
                op('E',e),
                op('C₃',r(z,120),'rotation',axis=z,angle=120),
                op('C₃²',r(z,240),'rotation',axis=z,angle=240),
                op('σₕ(xy)',m(z),'reflection',normal=z),
                op('S₃',s(z,120),'improper',axis=z,normal=z,angle=120),
                op('S₃⁵',s(z,240),'improper',axis=z,normal=z,angle=240),
            ]
            for i, angle in enumerate((90,210,330),1):
                a = np.radians(angle)
                axis = np.array([np.cos(a),np.sin(a),0.])
                normal = np.array([-np.sin(a),np.cos(a),0.])
                ops.extend([
                    op(f'C₂′({i})',r(axis,180),'rotation',axis=axis,angle=180),
                    op(f'σᵥ({i})',m(normal),'reflection',normal=normal),
                ])
            return ops
        if group == 'D2d':
            a = np.array([1.,1.,0.])
            b = np.array([1.,-1.,0.])
            return [
                op('E',e),
                op('C₂(z)',r(z,180),'rotation',axis=z,angle=180),
                op('C₂′(x=y)',r(a,180),'rotation',axis=a,angle=180),
                op('C₂′(x=−y)',r(b,180),'rotation',axis=b,angle=180),
                op('S₄',s(z,90),'improper',axis=z,normal=z,angle=90),
                op('S₄³',s(z,270),'improper',axis=z,normal=z,angle=270),
                op('σd(xz)',m(y),'reflection',normal=y),
                op('σd(yz)',m(x),'reflection',normal=x),
            ]
        raise ValueError(f'Неизвестная группа: {group}')
