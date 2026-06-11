# src/extractors/dfp_extractor.py (VERSÃO ATUALIZADA)
import requests
import zipfile
from pathlib import Path
from .base_extractor import BaseExtractor

class DFPExtractor(BaseExtractor):
    def __init__(self, config: dict, base_dir: Path):
        super().__init__(config, base_dir)
        self.ckan_api_url = f"https://dados.cvm.gov.br/api/3/action/package_show?id={self.config['ckan_id']}"

    def fetch_metadata(self) -> list:
        """Busca metadados do dataset na API do CKAN."""
        print(f"🔍 Consultando API do CKAN...")
        response = requests.get(self.ckan_api_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('success'):
            raise ValueError("Falha ao consultar a API do CKAN.")
            
        resources = data['result']['resources']
        zip_resources = [r for r in resources if r.get('format', '').lower() == 'zip']
        return zip_resources

    def is_downloaded(self, resource: dict) -> bool:
        """Verifica se um arquivo específico já foi baixado."""
        url = resource['url']
        file_name = url.split('/')[-1]
        dest_path = self.download_dir / file_name
        return dest_path.exists()

    def download_resources(self, resources: list) -> list:
        """Baixa os recursos (arquivos) para a pasta bronze."""
        downloaded_files = []
        
        for res in resources:
            url = res['url']
            file_name = url.split('/')[-1]
            dest_path = self.download_dir / file_name
            
            if dest_path.exists():
                print(f"⏭️  Arquivo já existe, pulando: {file_name}")
                downloaded_files.append(dest_path)
                continue
                
            print(f"⬇️  Baixando: {file_name}...")
            try:
                with requests.get(url, stream=True, timeout=120) as r:
                    r.raise_for_status()
                    with open(dest_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                downloaded_files.append(dest_path)
                self._extract_zip(dest_path)
                
            except Exception as e:
                print(f"❌ Erro ao baixar {file_name}: {e}")
                
        return downloaded_files

    def download_specific_resources(self, resources: list) -> list:
        """Baixa apenas os recursos especificados (sem verificar se já existem)."""
        downloaded_files = []
        
        for res in resources:
            url = res['url']
            file_name = url.split('/')[-1]
            dest_path = self.download_dir / file_name
            
            if dest_path.exists():
                print(f"⏭️  Arquivo já existe, pulando: {file_name}")
                downloaded_files.append(dest_path)
                continue
                
            print(f"⬇️  Baixando: {file_name}...")
            try:
                with requests.get(url, stream=True, timeout=120) as r:
                    r.raise_for_status()
                    with open(dest_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                downloaded_files.append(dest_path)
                self._extract_zip(dest_path)
                
            except Exception as e:
                print(f"❌ Erro ao baixar {file_name}: {e}")
                
        return downloaded_files

    def _extract_zip(self, zip_path: Path):
        """Descompacta o arquivo ZIP em uma pasta com o mesmo nome."""
        extract_dir = zip_path.parent / zip_path.stem
        extract_dir.mkdir(exist_ok=True)
        
        if any(extract_dir.iterdir()):
            return

        print(f"   🗜️  Descompactando: {zip_path.name}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)