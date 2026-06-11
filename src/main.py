# src/main.py
import sys
import yaml
from pathlib import Path

# Ajuste de caminho para garantir que os imports funcionem de qualquer lugar
sys.path.append(str(Path(__file__).resolve().parent))

from extractors.dfp_extractor import DFPExtractor

def main():
    # O diretório base é a raiz do projeto (cvm_data_warehouse)
    base_dir = Path(__file__).resolve().parent.parent
    
    # 1. Carregar configuração
    config_path = base_dir / "config" / "datasets.yaml"
    print(f"📖 Lendo configurações de: {config_path.name}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        
    # 2. Instanciar e rodar o extrator de DFP
    dfp_config = config['datasets']['dfp']
    extractor = DFPExtractor(dfp_config, base_dir)
    extractor.run()

if __name__ == "__main__":
    main()