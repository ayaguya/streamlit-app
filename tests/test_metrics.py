import os
import sys
import types
import importlib.util
import pandas as pd
import pytest

# Provide a minimal dummy streamlit module so app.py can be imported
class DummySidebar:
    def header(self, *args, **kwargs):
        pass
    def multiselect(self, *args, **kwargs):
        return []
    def slider(self, *args, **kwargs):
        return (0, 0)

def cache_data(func=None, **kwargs):
    if func is None:
        def decorator(f):
            return f
        return decorator
    return func

dummy_streamlit = types.SimpleNamespace(
    cache_data=cache_data,
    title=lambda *a, **k: None,
    header=lambda *a, **k: None,
    markdown=lambda *a, **k: None,
    plotly_chart=lambda *a, **k: None,
    dataframe=lambda *a, **k: None,
    warning=lambda *a, **k: None,
    sidebar=DummySidebar(),
)

sys.modules.setdefault("streamlit", dummy_streamlit)

# Load app.py from the subdirectory so we can access calculate_metrics
SPEC_PATH = os.path.join(os.path.dirname(__file__), "..", "streamlit-app", "app.py")
spec = importlib.util.spec_from_file_location("app_module", SPEC_PATH)
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)

calculate_metrics = app_module.calculate_metrics

@pytest.fixture
def sample_df():
    data = pd.DataFrame({
        "市町村": ["A", "A", "B", "B"],
        "年": [2020, 2021, 2020, 2021],
        "軒数": [10, 12, 8, 8],
    })
    return data

def test_calculate_metrics(sample_df):
    result = calculate_metrics(sample_df.copy(), "軒数")
    assert list(result["増減数"]) == [0, 2, 0, 0]
