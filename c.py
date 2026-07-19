from pathlib import Path

# Run this script from your project's root directory
ROOT = Path.cwd()

# ----------------------------
# Folders to create
# ----------------------------
folders = [
    ".github/workflows",
    ".streamlit",
    "app/agents",
    "app/nodes",
    "app/gateway",
    "app/guardrails",
    "app/ingestion",
    "app/services",
    "evals",
    "notebooks",
    "processed_data",
    "scripts",
    "tests",
    "ui",
]

# ----------------------------
# Files to create
# ----------------------------
files = [
    # .github
    ".github/workflows/cd.yml",
    ".github/workflows/ci.yml",

    # Streamlit
    ".streamlit/config.toml",

    # App - Agents
    "app/agents/planner.py",
    "app/agents/responder.py",
    "app/agents/retriever.py",

    # App - Nodes
    "app/nodes/graph.py",
    "app/nodes/state.py",

    # Gateway
    "app/gateway/__init__.py",
    "app/gateway/client.py",

    # Guardrails
    "app/guardrails/__init__.py",
    "app/guardrails/colang_rules.py",
    "app/guardrails/rails.py",

    # Services
    "app/services/__init__.py",

    # App root files
    "app/config.py",
    "app/health.py",
    "app/logging.py",
    "app/main.py",

    # Evals
    "evals/__init__.py",
    "evals/app.py",
    "evals/data_parser.py",
    "evals/golden_dataset.json",
    "evals/guardrails_eval.py",
    "evals/metrics.py",
    "evals/og_golden_dataset.json",
    "evals/pipeline.py",
    "evals/run_evals.py",

    # Scripts
    "scripts/aws_deploy_env.sh",
    "scripts/aws_deploy_state.sh",
    "scripts/aws_secret_arns.sh",
    "scripts/create_aws_secrets.py",
    "scripts/destroy_aws_deployment.sh",
    "scripts/list_portkey_configs.py",
    "scripts/locustfile.py",
    "scripts/render_task_defs.py",

    # Tests
    "tests/__init__.py",
    "tests/test_async_query.py",
    "tests/test_auth.py",
    "tests/test_checkpointer.py",
    "tests/test_connection_checker.py",
    "tests/test_evals.py",
    "tests/test_health.py",
    "tests/test_metrics.py",
    "tests/test_rate_limit.py",
    "tests/test_retry.py",

    # Root files
    ".dockerignore",
    ".env.example",
    ".gcloudignore",
    ".gitignore",
    "ARCHITECTURE.md",
    "Dockerfile",
    "README.md",
    "TESTING.md",
    "aws.md",
    "deployment_plan.md",
    "docker-compose.yml",
    "local_testing.md",
    "pyproject.toml",
    "requirements-prod.txt",
    "requirements.txt",
    "uv.lock",
]

# ----------------------------
# Create folders
# ----------------------------
for folder in folders:
    path = ROOT / folder
    path.mkdir(parents=True, exist_ok=True)

# ----------------------------
# Create files only if missing
# ----------------------------
for file in files:
    path = ROOT / file

    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.touch()
        print(f"Created: {file}")
    else:
        print(f"Skipped: {file}")

print("\n✅ Project structure checked successfully.")