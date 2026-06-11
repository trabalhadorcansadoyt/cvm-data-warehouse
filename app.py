# app.py
import streamlit as st
import yaml
from pathlib import Path
import pandas as pd
from src.extractors.dfp_extractor import DFPExtractor

# Configuração da página
st.set_page_config(page_title="CVM Data Warehouse Manager", layout="wide")

# Título
st.title("🏦 CVM Data Warehouse Manager")
st.markdown("Gerencie o download de dados da CVM de forma visual e interativa.")

# Carregar configuração
@st.cache_resource
def load_config():
    base_dir = Path(__file__).resolve().parent
    config_path = base_dir / "config" / "datasets.yaml"
    # 1. Verifica se o arquivo existe
    if not config_path.exists():
        st.error(f"❌ Arquivo de configuração não encontrado em: {config_path}")
        st.stop() # Para a execução do app
        
    try:
        # 2. Tenta ler o arquivo
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
            # 3. Verifica se o arquivo não está vazio
            if config is None:
                st.error("❌ O arquivo datasets.yaml está vazio ou com formatação inválida (verifique os espaços).")
                st.stop()
                
            return config, base_dir
            
    except Exception as e:
        st.error(f"❌ Erro ao ler o arquivo YAML: {e}")
        st.stop()

config, base_dir = load_config()

# Seleção de dataset (preparado para o futuro)
dataset_options = list(config['datasets'].keys())
selected_dataset = st.selectbox("Selecione o Dataset:", dataset_options)

if selected_dataset:
    dataset_config = config['datasets'][selected_dataset]
    
    # Instanciar extrator
    extractor = DFPExtractor(dataset_config, base_dir)
    
    # Botão para atualizar lista
    if st.button("🔄 Atualizar Lista de Arquivos"):
        st.cache_data.clear()
    
    # Buscar metadados
    @st.cache_data(ttl=3600)  # Cache por 1 hora
    def get_resources():
        return extractor.fetch_metadata()
    
    with st.spinner("Consultando API da CVM..."):
        try:
            resources = get_resources()
            
            # Criar DataFrame com status
            data = []
            for res in resources:
                file_name = res['url'].split('/')[-1]
                is_downloaded = extractor.is_downloaded(res)

                # 🛡️ CORREÇÃO À PROVA DE FALHAS
                raw_size = res.get('size')
                if raw_size is None or not isinstance(raw_size, (int, float)):
                    size_mb = 0.0
                else:
                    size_mb = round(raw_size / (1024 * 1024), 2)
                
                data.append({
                    'Arquivo': file_name,
                    'Status': '✅ Baixado' if is_downloaded else '⏳ Pendente',
                    'Tamanho (MB)': round(res.get('size', 0) / (1024*1024), 2),
                    'Formato': res.get('format', 'N/A'),
                    'URL': res['url'],
                    'resource_obj': res  # Guardamos o objeto completo para uso posterior
                })
            
            df = pd.DataFrame(data)
            
            # Estatísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Arquivos", len(df))
            with col2:
                st.metric("✅ Baixados", len(df[df['Status'] == '✅ Baixado']))
            with col3:
                st.metric("⏳ Pendentes", len(df[df['Status'] == '⏳ Pendente']))
            
            st.markdown("---")
            
            # Filtros
            st.subheader("🔍 Filtros")
            col1, col2 = st.columns(2)
            with col1:
                status_filter = st.multiselect(
                    "Filtrar por Status:",
                    options=['✅ Baixado', '⏳ Pendente'],
                    default=['✅ Baixado', '⏳ Pendente']
                )
            with col2:
                search_term = st.text_input("Buscar por nome do arquivo:")
            
            # Aplicar filtros
            filtered_df = df[df['Status'].isin(status_filter)]
            if search_term:
                filtered_df = filtered_df[filtered_df['Arquivo'].str.contains(search_term, case=False, na=False)]
            
            # Seleção de arquivos
            st.subheader("📥 Selecionar Arquivos para Download")
            
            # Checkbox para selecionar todos os pendentes
            select_all_pending = st.checkbox("Selecionar todos os pendentes")
            
            if select_all_pending:
                default_selection = filtered_df[filtered_df['Status'] == '⏳ Pendente'].index.tolist()
            else:
                default_selection = []
            
            # Tabela com checkboxes
            selected_indices = []
            for idx, row in filtered_df.iterrows():
                col1, col2, col3, col4 = st.columns([0.5, 3, 1, 1])
                with col1:
                    checked = st.checkbox("", key=f"check_{idx}", value=(idx in default_selection))
                    if checked:
                        selected_indices.append(idx)
                with col2:
                    st.write(row['Arquivo'])
                with col3:
                    st.write(row['Status'])
                with col4:
                    st.write(f"{row['Tamanho (MB)']} MB")
            
            # Botão de download
            st.markdown("---")
            if st.button(f"⬇️ Baixar {len(selected_indices)} arquivo(s) selecionado(s)", type="primary"):
                if len(selected_indices) == 0:
                    st.warning("Nenhum arquivo selecionado!")
                else:
                    selected_resources = [filtered_df.loc[idx, 'resource_obj'] for idx in selected_indices]
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    downloaded_count = 0
                    for i, res in enumerate(selected_resources):
                        file_name = res['url'].split('/')[-1]
                        status_text.text(f"Baixando {i+1}/{len(selected_resources)}: {file_name}")
                        
                        # Baixar arquivo individual
                        extractor.download_specific_resources([res])
                        downloaded_count += 1
                        progress_bar.progress((i + 1) / len(selected_resources))
                    
                    status_text.text(f"✅ Download concluído! {downloaded_count} arquivo(s) baixado(s).")
                    st.cache_data.clear()  # Limpar cache para atualizar status
                    st.success("Arquivos baixados com sucesso! Recarregue a página para ver o status atualizado.")
            
        except Exception as e:
            st.error(f"Erro ao consultar a API: {e}")