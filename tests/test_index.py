import pytest
import numpy as np
from index_engine.calculator import laspeyres_index, paasche_index, fisher_index

def test_laspeyres_index_known_values():
    # Base: route A = 100, route B = 200, weights: A=0.6, B=0.4
    # Current: route A = 110 (+10%), route B = 210 (+5%)
    # Base weighted sum = 0.6 * 100 + 0.4 * 200 = 60 + 80 = 140
    # Current weighted sum = 0.6 * 110 + 0.4 * 210 = 66 + 84 = 150
    # Laspeyres = (150 / 140) * 100 = 107.1428...
    weights = {("DEL", "BOM"): 0.6, ("DEL", "BLR"): 0.4}
    base_prices = {("DEL", "BOM"): 100.0, ("DEL", "BLR"): 200.0}
    current_prices = {("DEL", "BOM"): 110.0, ("DEL", "BLR"): 210.0}
    
    idx = laspeyres_index(current_prices, base_prices, weights)
    assert np.isclose(idx, (150.0 / 140.0) * 100)

def test_index_base_period_identity():
    weights = {("DEL", "BOM"): 0.7, ("BOM", "BLR"): 0.3}
    base_prices = {("DEL", "BOM"): 5000.0, ("BOM", "BLR"): 4000.0}
    
    lasp = laspeyres_index(base_prices, base_prices, weights)
    paas = paasche_index(base_prices, base_prices, weights)
    fish = fisher_index(lasp, paas)
    
    assert np.isclose(lasp, 100.0)
    assert np.isclose(paas, 100.0)
    assert np.isclose(fish, 100.0)

def test_fisher_ideal_property():
    lasp = 110.0
    paas = 105.0
    fish = fisher_index(lasp, paas)
    assert np.isclose(fish, np.sqrt(110.0 * 105.0))
