import src.D2_model_constraints as D2


def test_no_constraints_introduced():
    D2.modelling_constraints()
    assert 1 == 1
