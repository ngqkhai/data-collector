from pytest import fixture

@fixture
def sample_data():
    return {"key": "value"}

def test_service_functionality(sample_data):
    assert sample_data["key"] == "value"