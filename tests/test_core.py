from unittest.mock import MagicMock, patch

import pandas as pd

from core import generate_and_run


@patch("core.client.models.generate_content")
@patch("core.subprocess.run")
@patch("core.os.path.exists")
@patch("core.os.path.getsize")
@patch("core.pd.read_csv")
def test_generate_and_run_success(
    mock_read_csv, mock_getsize, mock_exists, mock_subprocess, mock_gemini
):

    mock_response = MagicMock()
    mock_response.text = "import pandas as pd\n# code..."
    mock_gemini.return_value = mock_response

    mock_docker_res = MagicMock()
    mock_docker_res.returncode = 0
    mock_subprocess.return_value = mock_docker_res

    mock_exists.return_value = True
    mock_getsize.return_value = 1000

    mock_df = pd.DataFrame([{"col1": "val1"}])
    mock_read_csv.return_value = mock_df

    # --- ЗАПУСК ТЕСТА ---
    result = generate_and_run(
        user_query="Test query", task_id=1, on_progress=lambda msg, p: None
    )

    # --- ПРОВЕРКИ ---
    assert result["status"] == "success"
    assert result["file"] == "storage/result_1.csv"
    assert "preview" in result
    assert result["row_count"] == 1

    mock_gemini.assert_called_once()
    mock_subprocess.assert_called_once()


@patch("core.client.models.generate_content")
@patch("core.subprocess.run")
def test_generate_and_run_docker_fail(mock_subprocess, mock_gemini):

    mock_response = MagicMock()
    mock_response.text = "bad code"
    mock_gemini.return_value = mock_response

    mock_docker_res = MagicMock()
    mock_docker_res.returncode = 1
    mock_docker_res.stderr = "SyntaxError"
    mock_subprocess.return_value = mock_docker_res

    result = generate_and_run("query", 1)

    assert mock_gemini.call_count == 3
    assert result["status"] == "error"
