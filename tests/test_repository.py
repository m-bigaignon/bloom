from sqlalchemy.orm import Session

from tests import model


def test_repository_can_save_a_batch(session: Session):
    batch = model.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)
    repo = 
