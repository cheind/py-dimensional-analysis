import pytest
#from functools import reduce
import numpy as np
from numpy.testing import assert_allclose

from .test_fixtures import *
from ..standard_systems import LMT, SI
from .. import meta
from .. import solver as slv
from .. import utils as u

def test_solve_e_has_zero_rows():
    # Number of solutions is 1 which makes e zero rows (no variables to choose freely).
    dm = np.array([
        [0.,1,0],   # M
        [1,1,-2],   # F
        [0,0,1]     # T
    ]).T # DxV
    P = slv.solve(dm, [1.,0, 0]) # PxV
    assert P.shape == (1,3)
    assert_allclose(P @ dm.T, [[1.,0, 0]]) # PxD

def test_solve_with_e():
    dm = np.array([
        [1.,1,0],
        [0,0,0],
        [0,0,0]
    ]) 
    # rank two, but A 2x2 will always be singular
    # if no column swap happens
    P = slv.solve(dm, [0,0,0.], strict=False)

@pytest.mark.usefixtures('dm_example_72')
def test_solve_72(dm_example_72):
    # No row deletion, no column swap
    P = slv.solve(dm_example_72, [3., 5., 7.])
    assert P.shape == (3,5)
    assert_allclose(P @ dm_example_72.T, np.tile([[3.,5.,7.]], (3,1))) # PxD


@pytest.mark.usefixtures('dm_example_72')
def test_solve_72_with_e(dm_example_72):
    # Explicitly specify matrix-e using the values from pp. 138
    opts = slv.SolverOptions(col_perm=range(5), e=np.array([[1, 0],[2, 0]]))
    P = slv.solve(dm_example_72, [3., 5., 7.], opts=opts)
    assert P.shape == (2,5)
    assert_allclose(P, [
        [1., 2, -1.8, 0.6, 0.2],
        [0,  0, 37/15., 6/15., -18/15.] 
    ])
        
@pytest.mark.usefixtures('dm_example_78')
def test_solve_78(dm_example_78):
    # Single row deletion
    P = slv.solve(dm_example_78, [2., 0, 0.])
    assert P.shape == (4,5)
    assert_allclose(P, [
        [ 1.,  0.,  0.,  0.,  1.],
        [ 0.,  1.,  0., -1.,  0.],
        [ 0.,  0.,  1.,  0.,  1.],
        [ 1.,  1.,  0., -1., -1.],
    ])
    assert_allclose(P @ dm_example_78.T, np.tile([[2.,0.,0.]], (4,1))) # PxD

@pytest.mark.usefixtures('dm_example_72')
def test_solver(dm_example_72):
    # Explicitly specify matrix-e using the values from pp. 138
    L,M,T = LMT.base_quantities()
    vs = LMT.qs_from_dm(dm_example_72) # Interpret dm in the LMT system
    s = slv.Solver(vs, LMT.q([3., 5., 7.]))
    assert s.variables == {
        'a': L*M**2*T**3, 
        'b': L**2*M**4*T**4, 
        'c': L**3*M**3*T**3, 
        'd': L**4*T**2, 
        'e': L**5*M**2*T}
    r = s.solve()
    assert_allclose(r.P @ dm_example_72.T, np.tile([[3.,5.,7.]], (3,1)))
    
    opts = slv.SolverOptions(col_perm=range(5), e=np.array([[1, 0],[2, 0]]))

    r = s.solve(select_values={'a':[1, 0], 'b':[2, 0]})
    assert r.P.shape == (2,5)
    assert_allclose(r.P, [
        [1., 2, -1.8, 0.6, 0.2],
        [0,  0, 37/15., 6/15., -18/15.] 
    ])

    r = s.solve(select_values={'d':[1], 'e':[2]})
    assert r.P.shape == (1,5)
    assert_allclose(r.P, [
        [2, 5, -7.666667, 1, 2],
    ])