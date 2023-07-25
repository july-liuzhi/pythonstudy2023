import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import spsolve
from fealpy.mesh import UniformMesh2d
from fealpy.decorator import cartesian
from typing import Callable, Tuple, Any
#类
class SinSinExpPDEData:
    def __init__(self, D=[0, 1, 0, 1], T=[0,0.1]):

        self._domain = D
        self._duration = T

    def domain(self):

        return self._domain

    def duration(self):

        return self._duration

    @cartesian
    def solution(self, p, t):

        pi = np.pi
        x = p[..., 0]
        y = p[..., 1]

        return np.sin(pi*x)*np.sin(pi*y)*np.exp(-2*pi*pi*t)

    @cartesian
    def init_solution(self, p):

        pi = np.pi
        x = p[..., 0]
        y = p[..., 1]
        return np.sin(pi*x)*np.sin(pi*y)

    @cartesian
    def source(self, p, t)->np.ndarray:
        pi = np.pi
        x = p[..., 0]
        y = p[..., 1]
        return np.zeros(x.shape)

    @cartesian
    def gradient(self, p, t):

        x = p[..., 0]
        y = p[..., 1]
        pi = np.pi
        val = np.zeros(p.shape, dtype=np.float64)
        val[..., 0] = pi*np.cos(pi*x)*np.sin(pi*y)*np.exp(-2*pi*pi*t)
        val[..., 1] = pi*np.sin(pi*x)*np.cos(pi*y)*np.exp(-2*pi*pi*t)
        return val

    @cartesian
    def dirichlet(self, p, t):

        return self.solution(p, t)
#实例
pde = SinSinExpPDEData()
#空间离散
domain = pde.domain()
nx = 20
ny = 20
hx = (domain[1] - domain[0])/nx
hy = (domain[3] - domain[2])/ny
mesh = UniformMesh2d([0, nx, 0, ny], h=(hx, hy), origin=(domain[0], domain[2]))
#时间离散
duration = pde.duration()
nt = 160
tau = (duration[1] - duration[0])/nt
#初值
uh0 = mesh.interpolate(pde.init_solution, intertype='node')
#向前欧拉方法
def advance_forward(n:np.int_)-> Tuple[np.ndarray, np.float64]: 
    t = duration[0] + n*tau
    if n == 0:
        return uh0, t
    else:
        A = mesh.parabolic_operator_forward(tau)

        source:Callable[[np.ndarray], np.ndarray] = lambda p: pde.source(p, t)
        f = mesh.interpolate(source, intertype='node')

        uh0[:].flat = A@uh0[:].flat + (tau*f[:]).flat
        gD:Callable[[np.ndarray], np.ndarray] = lambda p: pde.dirichlet(p, t)
        mesh.update_dirichlet_bc(gD, uh0)

        solution:Callable[[np.ndarray], np.ndarray] = lambda p: pde.solution(p, t)
        e = mesh.error(solution, uh0, errortype='max')
        print(f"the max error is {e}")
        return uh0, t
#热力图动画绘制
fig, axes = plt.subplots()
box = [0, 1, 0, 1, -1, 1] # 图像显示的范围 0 <= x <= 1, 0 <= y <= 1, -1 <= uh <= 1
mesh.show_animation(fig, axes, box, advance_forward, fname='parabolic_af.mp4', plot_type='imshow', frames=nt + 1)
plt.show()
