import io
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

SCRIPT = "from pages.dashboard import show_dashboard\nshow_dashboard()"


def test_sample_dashboard_and_empty_rack_selection():
    app = AppTest.from_string(SCRIPT).run(timeout=20)
    assert not app.exception
    assert app.metric[0].value == "Critical"
    assert app.metric[1].value == "92.0 °F"
    assert any("Demo data" in item.value for item in app.info)
    app.multiselect[0].set_value([]).run()
    assert not app.exception
    assert not app.metric
    assert any("Select at least one rack" in item.value for item in app.info)


def test_upload_prompt():
    app = AppTest.from_string(SCRIPT).run(timeout=20)
    app.radio[0].set_value("Upload CSV").run()
    assert not app.exception
    assert not app.metric
    assert any("Upload a CSV" in item.value for item in app.info)


def test_uploaded_multirack_data_and_filter():
    upload = io.StringIO("rack,temperature,humidity,power_kw\nA,92,45,3\nB,72,45,3\n")
    upload.name = "test.csv"
    app = AppTest.from_string(SCRIPT).run(timeout=20)
    with patch("pages.dashboard.st.file_uploader", return_value=upload):
        app.radio[0].set_value("Upload CSV").run()
    assert not app.exception
    assert app.metric[0].value == "Critical"
    upload.seek(0)
    with patch("pages.dashboard.st.file_uploader", return_value=upload):
        app.multiselect[0].set_value(["B"]).run()
    assert not app.exception
    assert app.metric[0].value == "Normal"
    assert app.dataframe[0].value["Rack"].tolist() == ["B"]


def test_invalid_upload_shows_error_without_metrics():
    upload = io.StringIO("unrecognized\nhello\n")
    upload.name = "invalid.csv"
    app = AppTest.from_string(SCRIPT).run(timeout=20)
    with patch("pages.dashboard.st.file_uploader", return_value=upload):
        app.radio[0].set_value("Upload CSV").run()
    assert not app.exception
    assert not app.metric
    assert any("No supported readings" in item.value for item in app.error)
