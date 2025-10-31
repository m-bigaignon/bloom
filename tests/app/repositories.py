from bloom.redbird.sqlrepo import SQLARepo
from tests.app.domain.model import Product


product_repo = SQLARepo(Product)
