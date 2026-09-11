from pathlib import Path
from streamlit.testing.v1 import AppTest


def test_main_shell_renders_all_workflows_without_credentials():
    app = AppTest.from_file(Path(__file__).parents[1] / "rackmind.py").run(timeout=30)
    assert not app.exception
    assert len(app.tabs) >= 5
