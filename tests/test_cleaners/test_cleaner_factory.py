import pytest
from services.data_collector.cleaner_factory import CleanerFactory

def test_cleaner_factory_creates_cleaner():
    factory = CleanerFactory()
    cleaner = factory.create_cleaner('type_a')
    assert cleaner is not None
    assert cleaner.type == 'type_a'

def test_cleaner_factory_invalid_type():
    factory = CleanerFactory()
    with pytest.raises(ValueError):
        factory.create_cleaner('invalid_type')