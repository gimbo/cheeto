import subprocess


def render_markdown(src: str) -> str:
    proc = subprocess.run(
        ["mdcat", "-"],
        capture_output=True,
        check=True,
        encoding="utf-8",
        input=src,
    )
    return proc.stdout
