# src/extractors/base_extractor.py
from abc import ABC, abstractmethod
from pathlib import Path

class BaseExtractor(ABC):
    def __init__(self, config: dict, base_dir: Path):
        self.config = config
        self.base_dir = base_dir
        # Define a pasta de destino (ex: cvm_data_warehouse/data/bronze/dfp)
        self.download_dir = base_dir / config.get('download_dir', 'data/bronze')
        self.download_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def fetch_metadata(self) -> list:
        """Busca metadados do dataset na API do CKAN."""
        pass

    @abstractmethod
    def download_resources(self, resources: list) -> list:
        """Baixa os recursos (arquivos) para a pasta bronze."""
        pass

    def run(self):
        """Executa o pipeline de extração."""
        print(f"🚀 Iniciando extração para: {self.config.get('name')}")
        resources = self.fetch_metadata()
        downloaded_files = self.download_resources(resources)
        print(f"✅ Extração concluída. {len(downloaded_files)} arquivos processados/baixados.\n")
        return downloaded_files