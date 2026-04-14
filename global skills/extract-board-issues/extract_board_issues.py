#!/usr/bin/env python3
"""
Extract Board Issues Skill - Extract GitHub Project Board issues into JSON

Usage:
    python3 extract_board_issues.py
    python3 extract_board_issues.py --repo goetz-kundenportal-phoenix
    python3 extract_board_issues.py --repo goetz-kundenportal-phoenix --board 5
    python3 extract_board_issues.py --dry-run

The script:
1. Detects the current repository (if in a git directory)
2. Detects the GitHub owner/organization
3. Retrieves all project boards associated with the repository
4. Presents board selection to user (interactive or via --board flag)
5. Extracts all issues from selected board
6. Saves structured JSON to /Users/admin/dev/Reports/{repo}/board-issues.json
"""

import json
import sys
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any
import argparse


class BoardExtractor:
    """Extract issues from GitHub Project Boards."""

    def __init__(self, repo_name: Optional[str] = None, dry_run: bool = False):
        """Initialize the extractor."""
        self.dry_run = dry_run
        self.repo_name = repo_name
        self.repo_owner = None
        
    def run_gh_command(self, cmd: List[str], silent: bool = False, timeout: int = 30) -> Optional[str]:
        """Run a gh CLI command and return output."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout
            )
            if result.returncode != 0:
                if not silent:
                    print(f"❌ Error running gh command: {' '.join(cmd)}")
                    if result.stderr:
                        print(f"   {result.stderr}")
                return None
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            if not silent:
                print(f"❌ Timeout running gh command (>30s): {' '.join(cmd)}")
            return None
        except Exception as e:
            if not silent:
                print(f"❌ Exception running gh command: {e}")
            return None

    def detect_repo_info(self) -> bool:
        """Detect repository name and owner from current directory."""
        if self.repo_name:
            # Already provided via argument
            return self._validate_repo_exists()
        
        # Try to detect from gh repo view
        print("⏳ Detecting repository...")
        repo_info = self.run_gh_command(["gh", "repo", "view", "--json", "name,owner"], silent=True)
        if not repo_info:
            print("❌ Could not detect repository. Are you in a git repository?")
            print("   Tip: Use --repo flag to specify repository name")
            return False
        
        try:
            data = json.loads(repo_info)
            self.repo_name = data["name"]
            self.repo_owner = data["owner"]["login"]
            return True
        except (json.JSONDecodeError, KeyError):
            return False

    def _validate_repo_exists(self) -> bool:
        """Validate that the specified repo exists."""
        if not self.repo_name:
            return False
        
        print(f"⏳ Validating repository: {self.repo_name}...")
        # Try to get repo info
        repo_info = self.run_gh_command(
            ["gh", "repo", "view", self.repo_name, "--json", "owner"],
            silent=True
        )
        if repo_info:
            try:
                data = json.loads(repo_info)
                self.repo_owner = data["owner"]["login"]
                return True
            except (json.JSONDecodeError, KeyError):
                pass
        
        # If validation fails, try just trusting the repo name for now
        # (gh api will validate it later)
        print(f"⚠️  Could not validate repository: {self.repo_name}")
        print(f"    Will proceed - gh api will validate")
        return True

    def validate_auth(self) -> bool:
        """Validate that gh CLI is authenticated."""
        auth_info = self.run_gh_command(["gh", "auth", "status"], silent=True)
        if not auth_info:
            print("❌ GitHub CLI is not authenticated.")
            print("   Run: gh auth login")
            return False
        return True

    def get_repo_boards(self) -> Optional[List[Dict[str, Any]]]:
        """Get all project boards associated with the repository."""
        if not self.repo_name:
            return None
        
        # If repo_owner is not set, try to detect it now
        if not self.repo_owner:
            print(f"⏳ Detecting repository owner...")
            repo_info = self.run_gh_command(
                ["gh", "repo", "view", self.repo_name, "--json", "owner"],
                silent=True
            )
            if repo_info:
                try:
                    data = json.loads(repo_info)
                    self.repo_owner = data["owner"]["login"]
                except (json.JSONDecodeError, KeyError):
                    pass
        
        if not self.repo_owner:
            print(f"❌ Could not detect repository owner")
            return None
        
        print(f"⏳ Fetching project boards for {self.repo_owner}/{self.repo_name}...")
        
        query = """
        query($owner: String!, $name: String!) {
          repository(owner: $owner, name: $name) {
            projectsV2(first: 20) {
              nodes {
                id
                title
                items(first: 1) {
                  totalCount
                }
              }
            }
          }
        }
        """
        
        result = self.run_gh_command([
            "gh", "api", "graphql",
            "-f", f"owner={self.repo_owner}",
            "-f", f"name={self.repo_name}",
            "-f", f"query={query}"
        ], silent=False, timeout=60)
        
        if not result:
            print("❌ Failed to fetch boards. Check your GitHub authentication.")
            return None
        
        try:
            data = json.loads(result)
            if "errors" in data:
                print(f"❌ GraphQL Error: {data['errors']}")
                return None
            
            boards = data.get("data", {}).get("repository", {}).get("projectsV2", {}).get("nodes", [])
            return boards
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse GraphQL response: {e}")
            return None

    def select_board(self, boards: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Present board selection to user."""
        if not boards:
            print("❌ No boards found")
            return None
        
        if len(boards) == 1:
            # For single board, still ask for confirmation
            print(f"\n✅ Found 1 board: {boards[0]['title']}")
            confirm = input("   Use this board? (y/n): ").strip().lower()
            if confirm == 'y':
                return boards[0]
            return None
        
        print(f"\n📋 Found {len(boards)} board(s):\n")
        
        # Show all options
        for i, board in enumerate(boards, 1):
            item_count = board.get('items', {}).get('totalCount', 0)
            print(f"  {i}. {board['title']}")
            print(f"     ({item_count} items)")
        
        # Get selection
        while True:
            try:
                choice = input(f"\n🎯 Select board number (1-{len(boards)}): ").strip()
                board_idx = int(choice) - 1
                if 0 <= board_idx < len(boards):
                    return boards[board_idx]
                else:
                    print(f"❌ Please enter a number between 1 and {len(boards)}")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")

    def extract_issues(self, board_id: str) -> Optional[List[Dict[str, Any]]]:
        """Extract issues from a project board with pagination."""
        all_issues = []
        has_next_page = True
        end_cursor = None
        page_count = 0
        
        while has_next_page:
            page_count += 1
            cursor_arg = f', after: "{end_cursor}"' if end_cursor else ''
            
            query = f"""
            query {{
              node(id: "{board_id}") {{
                ... on ProjectV2 {{
                  items(first: 50{cursor_arg}) {{
                    pageInfo {{
                      hasNextPage
                      endCursor
                    }}
                    nodes {{
                      id
                      content {{
                        __typename
                        ... on Issue {{
                          number
                          title
                          body
                          state
                          createdAt
                          updatedAt
                          comments(first: 20) {{
                            nodes {{
                              author {{
                                login
                              }}
                              body
                              createdAt
                            }}
                          }}
                        }}
                      }}
                    }}
                  }}
                }}
              }}
            }}
            """
            
            result = self.run_gh_command([
                "gh", "api", "graphql",
                "-f", f"query={query}"
            ], silent=False, timeout=60)
            
            if not result:
                print("❌ Failed to extract issues")
                return None
            
            try:
                data = json.loads(result)
                
                if "errors" in data:
                    print(f"❌ GraphQL Error: {data['errors']}")
                    return None
                
                items = data.get('data', {}).get('node', {}).get('items', {}).get('nodes', [])
                
                # Filter to only Issue items (exclude DraftIssue)
                issues_in_page = 0
                for item in items:
                    content = item.get('content', {})
                    if content.get('__typename') == 'Issue':
                        all_issues.append(content)
                        issues_in_page += 1
                
                pageInfo = data.get('data', {}).get('node', {}).get('items', {}).get('pageInfo', {})
                has_next_page = pageInfo.get('hasNextPage', False)
                end_cursor = pageInfo.get('endCursor', None)
                
                print(f"⏳ Page {page_count}: Extracted {issues_in_page} issues (total: {len(all_issues)})")
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse GraphQL response: {e}")
                return None
        
        return all_issues

    def save_json(self, board_name: str, issues: List[Dict[str, Any]]) -> bool:
        """Save extracted issues to JSON file."""
        output_dir = Path(f"/Users/admin/dev/Reports/{self.repo_name}")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "board-issues.json"
        
        # Clean up issue structure (remove __typename)
        cleaned_issues = []
        for issue in issues:
            cleaned_issue = {
                "number": issue.get("number"),
                "title": issue.get("title"),
                "body": issue.get("body"),
                "state": issue.get("state"),
                "createdAt": issue.get("createdAt"),
                "updatedAt": issue.get("updatedAt"),
                "comments": self._format_comments(issue.get("comments", {}).get("nodes", []))
            }
            cleaned_issues.append(cleaned_issue)
        
        data = {
            "repository": f"{self.repo_owner}/{self.repo_name}",
            "board_name": board_name,
            "extracted_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "total_issues": len(cleaned_issues),
            "issues": cleaned_issues
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"\n✅ Extraction complete!")
            print(f"   📁 Saved to: {output_file}")
            print(f"   📊 Total issues: {len(cleaned_issues)}")
            return True
        except Exception as e:
            print(f"❌ Failed to save JSON: {e}")
            return False

    def _format_comments(self, comment_nodes: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Format comments for output."""
        comments = []
        for node in comment_nodes:
            author = node.get('author', {})
            comments.append({
                "author": author.get('login', 'unknown'),
                "body": node.get('body', ''),
                "created_at": node.get('createdAt', '')
            })
        return comments

    def run(self, board_index: Optional[int] = None) -> bool:
        """Main execution flow."""
        print("🔍 Extract Board Issues\n")
        
        # Step 1: Detect repository
        if not self.detect_repo_info():
            return False
        print(f"✅ Repository: {self.repo_name}")
        print(f"✅ Owner: {self.repo_owner}")
        
        # Step 2: Validate authentication
        if not self.validate_auth():
            return False
        print("✅ GitHub authentication valid")
        
        if self.dry_run:
            print("\n✅ Dry run complete - all validations passed")
            return True
        
        # Step 3: Get boards associated with the repository
        boards = self.get_repo_boards()
        if not boards:
            print("❌ Could not fetch boards or no boards found for this repository")
            return False
        
        print(f"✅ Found {len(boards)} board(s)")
        
        # Step 4: Select board
        if board_index is not None:
            # Use provided index
            if 0 <= board_index < len(boards):
                selected_board = boards[board_index]
            else:
                print(f"❌ Invalid board index {board_index + 1}")
                return False
        else:
            # Interactive selection
            selected_board = self.select_board(boards)
            if not selected_board:
                print("❌ No board selected")
                return False
        
        print(f"\n📋 Selected board: {selected_board['title']}")
        
        # Step 5: Extract issues
        print("⏳ Extracting issues...")
        issues = self.extract_issues(selected_board["id"])
        if issues is None:
            return False
        
        if not issues:
            print("⚠️  No issues found in board")
        else:
            print(f"✅ Found {len(issues)} issue(s)")
        
        # Step 6: Save JSON
        return self.save_json(selected_board["title"], issues)


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Extract GitHub Project Board issues into JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 extract_board_issues.py                                    # Auto-detect and interactive
  python3 extract_board_issues.py --repo goetz-kundenportal-phoenix  # Specify repo
  python3 extract_board_issues.py --board 5                          # Select board 5
  python3 extract_board_issues.py --dry-run                          # Validate auth only
        """
    )
    
    parser.add_argument(
        "--repo",
        help="Repository name (auto-detected if not provided)"
    )
    parser.add_argument(
        "--owner",
        help="Repository owner/organization (auto-detected if not provided)"
    )
    parser.add_argument(
        "--board",
        type=int,
        help="Board index to use (1-based, starting from 1). If not provided, interactive selection is offered."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate authentication and boards without extraction"
    )
    
    args = parser.parse_args()
    
    extractor = BoardExtractor(
        repo_name=args.repo,
        dry_run=args.dry_run
    )
    
    # Set owner if provided
    if args.owner:
        extractor.repo_owner = args.owner
    
    # Convert 1-based board index to 0-based
    board_index = args.board - 1 if args.board else None
    
    success = extractor.run(board_index=board_index)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
