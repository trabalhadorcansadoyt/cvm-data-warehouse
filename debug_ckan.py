import requests

url = "https://dados.cvm.gov.br/api/3/action/package_show?id=cia_aberta-doc-dfp"
print("🔍 Consultando a API da CVM...\n")

response = requests.get(url, timeout=30)
data = response.json()

if data.get('success'):
    resources = data['result']['resources']
    print(f"✅ Sucesso! Total de recursos encontrados: {len(resources)}\n")
    
    print("--- Analisando os primeiros 3 recursos ---")
    for i, res in enumerate(resources[:3]):
        print(f"Recurso {i+1}:")
        print(f"  URL: {res.get('url')}")
        
        # Aqui está o segredo: vamos ver o TIPO e o VALOR exato do campo 'size'
        raw_size = res.get('size')
        print(f"  Tipo do dado 'size': {type(raw_size)}")
        print(f"  Valor do dado 'size': {raw_size}")
        print("-" * 50)
else:
    print("❌ Falha na API:", data)