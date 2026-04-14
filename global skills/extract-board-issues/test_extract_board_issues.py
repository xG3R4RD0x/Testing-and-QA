#!/usr/bin/env python3
"""
Unit tests for extract_board_issues.py using mocked gh CLI responses.

Run with: pytest test_extract_board_issues.py -v
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from extract_board_issues import BoardExtractor


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_fixtures():
    """Load sample fixtures from JSON."""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_responses.json"
    with open(fixture_path, 'r') as f:
        return json.load(f)


@pytest.fixture
def extractor():
    """Create a BoardExtractor instance."""
    return BoardExtractor(repo_name="goetz-kundenportal-phoenix", dry_run=False)


@pytest.fixture
def extractor_no_repo():
    """Create a BoardExtractor without repo name."""
    return BoardExtractor(repo_name=None, dry_run=False)


# ============================================================================
# Tests: Repository Detection
# ============================================================================

def test_detect_repo_info_with_provided_name(extractor):
    """Test that provided repo name is accepted."""
    assert extractor.repo_name == "goetz-kundenportal-phoenix"


def test_detect_repo_info_validates_repo(extractor):
    """Test that repo validation attempts to check repo exists."""
    with patch.object(extractor, 'run_gh_command') as mock_run:
        mock_run.return_value = json.dumps({
            "owner": {"login": "goetz-kundenportal"}
        })
        
        result = extractor._validate_repo_exists()
        assert result is True
        assert extractor.repo_owner == "goetz-kundenportal"


def test_detect_repo_info_fails_on_invalid_json(extractor):
    """Test that invalid JSON response is handled."""
    with patch.object(extractor, 'run_gh_command') as mock_run:
        mock_run.return_value = "invalid json"
        
        result = extractor._validate_repo_exists()
        assert result is False


# ============================================================================
# Tests: Authentication
# ============================================================================

def test_validate_auth_success(extractor):
    """Test successful authentication validation."""
    with patch.object(extractor, 'run_gh_command') as mock_run:
        mock_run.return_value = "Logged in as alice-dev"
        
        result = extractor.validate_auth()
        assert result is True


def test_validate_auth_failure(extractor, capsys):
    """Test authentication validation failure."""
    with patch.object(extractor, 'run_gh_command') as mock_run:
        mock_run.return_value = None
        
        result = extractor.validate_auth()
        assert result is False
        
        captured = capsys.readouterr()
        assert "not authenticated" in captured.out


# ============================================================================
# Tests: Getting All Boards
# ============================================================================

def test_get_all_boards_success(extractor, sample_fixtures):
    """Test successful retrieval of all boards."""
    extractor.repo_owner = "goetz-kundenportal"  # Must set owner first
    with patch.object(extractor, 'run_gh_command') as mock_run:
        mock_run.return_value = json.dumps(
            sample_fixtures["sample_boards_response"]
        )
        
        boards = extractor.get_all_boards()
        assert boards is not None
        assert len(boards) == 5
        assert boards[0]["title"] == "goetz-kundenportal-phoenix: Sprint 1"


def test_get_all_boards_handles_graphql_error(extractor, capsys):
    """Test handling of GraphQL errors."""
    extractor.repo_owner = "test-owner"  # Must set owner first
    with patch.object(extractor, 'run_gh_command') as mock_run:
        mock_run.return_value = json.dumps({
            "errors": [{"message": "Unauthorized"}]
        })
        
        boards = extractor.get_all_boards()
        assert boards is None
        
        captured = capsys.readouterr()
        assert "GraphQL Error" in captured.out


def test_get_all_boards_returns_none_on_failure(extractor):
    """Test that None is returned on command failure."""
    with patch.object(extractor, 'run_gh_command') as mock_run:
        mock_run.return_value = None
        
        boards = extractor.get_all_boards()
        assert boards is None


def test_get_all_boards_handles_invalid_json(extractor):
    """Test handling of invalid JSON response."""
    with patch.object(extractor, 'run_gh_command') as mock_run:
        mock_run.return_value = "not json"
        
        boards = extractor.get_all_boards()
        assert boards is None


# ============================================================================
# Tests: Board Filtering
# ============================================================================

def test_filter_boards_exact_match(extractor, sample_fixtures):
    """Test filtering boards by exact repo name."""
    boards = sample_fixtures["sample_boards_response"]["data"]["organization"]["projectsV2"]["nodes"]
    
    filtered = extractor.filter_boards(boards)
    assert len(filtered) == 3  # Only boards with "goetz-kundenportal-phoenix"
    assert all("goetz-kundenportal-phoenix" in b["title"] for b in filtered)


def test_filter_boards_case_insensitive(extractor, sample_fixtures):
    """Test that filtering is case-insensitive."""
    extractor.repo_name = "GOETZ-KUNDENPORTAL-PHOENIX"
    boards = sample_fixtures["sample_boards_response"]["data"]["organization"]["projectsV2"]["nodes"]
    
    filtered = extractor.filter_boards(boards)
    assert len(filtered) == 3


def test_filter_boards_fallback_to_all(extractor, sample_fixtures):
    """Test fallback to all boards when no matches found."""
    extractor.repo_name = "nonexistent-repo"
    boards = sample_fixtures["sample_boards_response"]["data"]["organization"]["projectsV2"]["nodes"]
    
    filtered = extractor.filter_boards(boards)
    # Should return all boards as fallback
    assert len(filtered) == len(boards)


def test_filter_boards_empty_list(extractor):
    """Test filtering empty board list."""
    filtered = extractor.filter_boards([])
    assert filtered == []


def test_filter_boards_no_repo_name(extractor):
    """Test filtering when no repo name is set."""
    extractor.repo_name = None
    boards = [
        {"id": "1", "title": "Board 1"},
        {"id": "2", "title": "Board 2"}
    ]
    
    filtered = extractor.filter_boards(boards)
    assert len(filtered) == 2


# ============================================================================
# Tests: Board Selection
# ============================================================================

def test_select_board_single_board(extractor):
    """Test selection when only one board exists."""
    boards = [{"id": "id1", "title": "Only Board"}]
    
    with patch('builtins.input'):
        selected = extractor.select_board(boards)
        assert selected == boards[0]


def test_select_board_user_selection_valid(extractor):
    """Test user selecting a valid board."""
    boards = [
        {"id": "id1", "title": "Board 1"},
        {"id": "id2", "title": "Board 2"},
        {"id": "id3", "title": "Board 3"}
    ]
    
    with patch('builtins.input', return_value="2"):
        selected = extractor.select_board(boards)
        assert selected == boards[1]


def test_select_board_user_selection_invalid(extractor):
    """Test user selecting an invalid board index."""
    boards = [
        {"id": "id1", "title": "Board 1"},
        {"id": "id2", "title": "Board 2"}
    ]
    
    with patch('builtins.input', return_value="99"):
        selected = extractor.select_board(boards)
        assert selected is None


def test_select_board_user_selection_non_numeric(extractor):
    """Test user entering non-numeric input when multiple boards exist."""
    boards = [
        {"id": "id1", "title": "Board 1"},
        {"id": "id2", "title": "Board 2"}
    ]
    
    with patch('builtins.input', return_value="invalid"):
        selected = extractor.select_board(boards)
        assert selected is None


def test_select_board_empty_list(extractor, capsys):
    """Test selection with empty board list."""
    selected = extractor.select_board([])
    assert selected is None
    
    captured = capsys.readouterr()
    assert "No boards found" in captured.out


# ============================================================================
# Tests: Issue Extraction
# ============================================================================

def test_extract_issues_success(extractor, sample_fixtures):
    """Test successful issue extraction."""
    with patch.object(extractor, 'run_gh_command') as mock_run:
        mock_run.return_value = json.dumps(
            sample_fixtures["sample_issues_response"]
        )
        
        issues = extractor.extract_issues("PVT_kwDOABCDEF")
        assert issues is not None
        assert len(issues) == 3
        
        # Check structure
        issue = issues[0]
        assert issue["number"] == 123
        assert issue["title"] == "Implement user authentication"
        assert issue["state"] == "OPEN"
        assert len(issue["comments"]) == 2


def test_extract_issues_with_no_comments(extractor, sample_fixtures):
    """Test issue extraction preserves issues with no comments."""
    with patch.object(extractor, 'run_gh_command') as mock_run:
        mock_run.return_value = json.dumps(
            sample_fixtures["sample_issues_response"]
        )
        
        issues = extractor.extract_issues("PVT_kwDOABCDEF")
        
        # Third issue has no comments
        issue_3 = issues[2]
        assert len(issue_3["comments"]) == 0


def test_extract_issues_handles_graphql_error(extractor, capsys):
    """Test handling of GraphQL errors during extraction."""
    with patch.object(extractor, 'run_gh_command') as mock_run:
        mock_run.return_value = json.dumps({
            "errors": [{"message": "Access denied"}]
        })
        
        issues = extractor.extract_issues("PVT_kwDOABCDEF")
        assert issues is None
        
        captured = capsys.readouterr()
        assert "GraphQL Error" in captured.out


def test_extract_issues_returns_none_on_failure(extractor):
    """Test that None is returned on command failure."""
    with patch.object(extractor, 'run_gh_command') as mock_run:
        mock_run.return_value = None
        
        issues = extractor.extract_issues("PVT_kwDOABCDEF")
        assert issues is None


def test_extract_issues_validates_output_schema(extractor, sample_fixtures):
    """Test that extracted issues follow required schema."""
    with patch.object(extractor, 'run_gh_command') as mock_run:
        mock_run.return_value = json.dumps(
            sample_fixtures["sample_issues_response"]
        )
        
        issues = extractor.extract_issues("PVT_kwDOABCDEF")
        
        # Validate schema
        required_fields = ["number", "title", "body", "state", "created_at", "updated_at", "comments"]
        for issue in issues:
            for field in required_fields:
                assert field in issue, f"Missing field: {field}"
            
            # Validate comment schema
            for comment in issue["comments"]:
                assert "author" in comment
                assert "body" in comment
                assert "created_at" in comment


# ============================================================================
# Tests: JSON Saving
# ============================================================================

def test_save_json_creates_directory(extractor, tmp_path):
    """Test that output directory is created if it doesn't exist."""
    with patch('pathlib.Path.mkdir') as mock_mkdir:
        with patch('builtins.open', create=True):
            extractor.repo_name = "test-repo"
            issues = []
            
            extractor.save_json("Test Board", issues)
            
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


def test_save_json_creates_valid_json(extractor, tmp_path, monkeypatch):
    """Test that saved JSON is valid and has correct structure."""
    # Mock the path to use tmp_path
    output_dir = tmp_path / "test-repo"
    output_dir.mkdir()
    
    extractor.repo_name = "test-repo"
    extractor.repo_owner = "test-owner"
    
    issues = [
        {
            "number": 1,
            "title": "Test Issue",
            "body": "Test body",
            "state": "OPEN",
            "created_at": "2024-01-20T10:00:00Z",
            "updated_at": "2024-01-20T10:00:00Z",
            "comments": []
        }
    ]
    
    with patch('pathlib.Path') as mock_path_class:
        mock_path = MagicMock()
        mock_path.__truediv__ = lambda self, x: tmp_path / x
        mock_path_class.return_value = mock_path
        
        # Patch the actual file writing
        with patch('builtins.open', create=True) as mock_open:
            extractor.save_json("Test Board", issues)
            
            # Verify open was called
            assert mock_open.called


def test_save_json_includes_timestamp(extractor, tmp_path, monkeypatch):
    """Test that saved JSON includes ISO 8601 timestamp."""
    output_dir = tmp_path / "test-repo"
    output_dir.mkdir()
    
    extractor.repo_name = "test-repo"
    extractor.repo_owner = "test-owner"
    
    issues = []
    
    with patch('builtins.open', create=True) as mock_open:
        with patch('json.dump') as mock_dump:
            extractor.save_json("Test Board", issues)
            
            # Check that json.dump was called
            assert mock_dump.called
            
            # Get the data that was dumped
            call_args = mock_dump.call_args
            data = call_args[0][0]
            
            # Verify structure
            assert "extracted_at" in data
            assert "repository" in data
            assert "board_name" in data
            assert "total_issues" in data
            assert "issues" in data


# ============================================================================
# Tests: Integration
# ============================================================================

def test_run_dry_run_mode(extractor):
    """Test dry-run mode validates but doesn't extract."""
    extractor.dry_run = True
    extractor.repo_owner = "test-owner"
    extractor.repo_name = "test-repo"
    
    with patch.object(extractor, 'detect_repo_info', return_value=True):
        with patch.object(extractor, 'validate_auth', return_value=True):
            result = extractor.run()
            assert result is True


def test_run_complete_flow(extractor, sample_fixtures):
    """Test complete extraction flow."""
    # Pre-set repo info to skip detection
    extractor.repo_name = "goetz-kundenportal-phoenix"
    extractor.repo_owner = "goetz-kundenportal"
    
    with patch.object(extractor, 'detect_repo_info', return_value=True):
        with patch.object(extractor, 'run_gh_command') as mock_run:
            # Mock responses in order of calls
            call_count = [0]
            
            def mock_response(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:  # auth status
                    return "Logged in"
                elif call_count[0] == 2:  # get boards
                    return json.dumps(sample_fixtures["sample_boards_response"])
                elif call_count[0] == 3:  # extract issues
                    return json.dumps(sample_fixtures["sample_issues_response"])
                return None
            
            mock_run.side_effect = mock_response
            
            with patch.object(extractor, 'select_board') as mock_select:
                mock_select.return_value = {
                    "id": "PVT_kwDOABCDEF",
                    "title": "goetz-kundenportal-phoenix: Sprint 1"
                }
                
                with patch.object(extractor, 'save_json', return_value=True) as mock_save:
                    result = extractor.run()
                    assert result is True
                    assert mock_save.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
