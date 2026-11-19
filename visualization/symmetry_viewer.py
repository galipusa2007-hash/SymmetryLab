import numpy as np
import plotly.graph_objects as go

class SymmetryViewer:
    @staticmethod
    def add_axis(fig, axis, length=2.8):
        axis = np.asarray(axis,dtype=float)
        axis = axis / np.linalg.norm(axis)
        lo,hi = -length*axis,length*axis
        fig.add_trace(go.Scatter3d(x=[lo[0],hi[0]],y=[lo[1],hi[1]],z=[lo[2],hi[2]],
                                   mode='lines',line=dict(color='#ef4444',width=5,dash='dash'),
                                   name='Ось вращения',hoverinfo='skip'))

    @staticmethod
    def add_plane(fig, normal, size=2.5):
        n=np.asarray(normal,dtype=float)
        n=n/np.linalg.norm(n)
        helper=np.array([1.,0.,0.])
        if abs(np.dot(helper,n))>.9:
            helper=np.array([0.,1.,0.])
        u=np.cross(n,helper)
        u=u/np.linalg.norm(u)
        v=np.cross(n,u)
        p=np.array([-u-v,u-v,u+v,-u+v])*size
        fig.add_trace(go.Mesh3d(x=p[:,0],y=p[:,1],z=p[:,2],i=[0,0],j=[1,2],k=[2,3],
                                opacity=.17,color='#00bcd4',name='Плоскость отражения',hoverinfo='skip'))

    @staticmethod
    def add_element(fig,operation):
        if operation.kind in ('rotation','improper'):
            SymmetryViewer.add_axis(fig,operation.axis)
        if operation.kind in ('reflection','improper'):
            SymmetryViewer.add_plane(fig,operation.normal)
        if operation.kind=='inversion':
            fig.add_trace(go.Scatter3d(x=[0],y=[0],z=[0],mode='markers',
                                       marker=dict(color='yellow',size=9),name='Центр инверсии'))
        return fig
