from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import kagglehub


@dataclass
class KaggleDatasetDownloader:
    dataset_slug: str
    output_path: Path

    def download_and_place(self) -> Path:
        dataset_dir = Path(kagglehub.dataset_download(self.dataset_slug))
        csv_files = list(dataset_dir.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {dataset_dir}")

        # Pick the largest CSV in the dataset directory as the main file.
        source = max(csv_files, key=lambda p: p.stat().st_size)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        source.replace(self.output_path)
        return self.output_path

