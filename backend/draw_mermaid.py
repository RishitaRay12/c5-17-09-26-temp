import subprocess
from pathlib import Path
from app.graph import app


def main():
    # ---------------------------------------------------------
    # Generate Mermaid content from the actual LangGraph
    # ---------------------------------------------------------

    mermaid = app.get_graph().draw_mermaid()

    # Project root
    project_root = (
        Path(__file__).resolve().parent.parent
    )

    # Output files
    mmd_file = project_root / "langgraph_workflow.mmd"
    png_file = project_root / "langgraph_workflow.png"

    # ---------------------------------------------------------
    # Save Mermaid file
    # ---------------------------------------------------------

    mmd_file.write_text(
        mermaid,
        encoding="utf-8",
    )

    print(
        f"Mermaid file generated: {mmd_file}"
    )

    # ---------------------------------------------------------
    # Generate PNG image
    # ---------------------------------------------------------

    try:
        subprocess.run(
            [
                "npx",
                "-p",
                "@mermaid-js/mermaid-cli",
                "mmdc",
                "-i",
                str(mmd_file),
                "-o",
                str(png_file),
            ],
            check=True,
            shell=True
        )

        print(
            f"PNG image generated: {png_file}"
        )

    except subprocess.CalledProcessError as exc:
        print(
            "Could not generate PNG image."
        )
        print(exc)

    print(
        "\nWorkflow diagram generation completed."
    )


if __name__ == "__main__":
    main()