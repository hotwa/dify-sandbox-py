import sys
import os
import asyncio

SRC_PATH = os.path.join("/app", "mcp-terminal", "src")
sys.path.insert(0, SRC_PATH)

from mcp_terminal.tools.terminal import TerminalTool
from gitingest import ingest

DEFAULT_CLONE_URL = "https://github.com/hotwa/dify-sandbox-py"
DEFAULT_LOCAL_PATH = "/app/repo/dify-sandbox-py"
DEFAULT_INCLUDE_PATTERNS = ""
DEFAULT_EXCLUDE_PATTERNS = {"*.pyc"}
DEFAULT_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

async def ensure_repo_latest(clone_url: str, local_path: str, timeout: int = 600) -> str:
    terminal_tool = TerminalTool(controller_type="subprocess")
    if os.path.exists(local_path) and os.path.isdir(local_path):
        print(f"Repo exists at {local_path}, running git pull ...")
        cmd = f"cd {local_path} && git pull"
    else:
        print(f"Repo not found at {local_path}, cloning ...")
        cmd = f"git clone {clone_url} {local_path}"
    result = await terminal_tool.controller.execute_command(
        cmd, wait_for_output=True, timeout=timeout
    )
    return result

def ingest_repo(
    local_path: str,
    include_patterns: str = DEFAULT_INCLUDE_PATTERNS,
    exclude_patterns: set = DEFAULT_EXCLUDE_PATTERNS,
    max_file_size: int = DEFAULT_MAX_FILE_SIZE
) -> dict:
    # 若在Jupyter/IPython环境，需用nest_asyncio防止event loop报错
    try:
        import nest_asyncio
        nest_asyncio.apply()
    except ImportError:
        pass

    summary, tree, content = ingest(
        local_path,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        max_file_size=max_file_size
    )
    return {
        "summary": summary,
        "tree": tree,
        "content": content
    }

async def main(
    clone_url: str = DEFAULT_CLONE_URL,
    local_path: str = DEFAULT_LOCAL_PATH,
    include_patterns: str = DEFAULT_INCLUDE_PATTERNS,
    exclude_patterns: set = DEFAULT_EXCLUDE_PATTERNS,
    max_file_size: int = DEFAULT_MAX_FILE_SIZE
) -> dict:
    # 1. 拉取/克隆仓库
    clone_result = await ensure_repo_latest(clone_url, local_path)
    print(f"Git operation result:\n{clone_result}\n")
    if not clone_result.get("success", True):
        raise Exception("Git操作失败，退出")

    # 2. 分析仓库
    print(f"Ingesting repo at {local_path} ...")
    ingest_result = ingest_repo(
        local_path,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        max_file_size=max_file_size
    )
    print("Ingest result summary:", ingest_result["summary"])

    # 3. 返回所需数据
    return {
        "repo_path": local_path,
        "summary": ingest_result["summary"],
        "tree": ingest_result["tree"],
        "content": ingest_result["content"]
    }

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    final_result = asyncio.run(main())
    # 这里你可以直接打印，或者进一步处理final_result
    print("\n======= FINAL RESULT =======")
    print(f"Repo Path: {final_result['repo_path']}")

