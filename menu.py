# menu.py - CLIENTE CLI INTERATIVO
import requests
from time import sleep

BASE_URL = "http://127.0.0.1:5000"

def safe_request(method, endpoint, **kwargs):
    """
    Faz uma requisição HTTP com tratamento de erros
    Retorna a resposta JSON ou None em caso de erro
    """
    url = f"{BASE_URL}{endpoint}"
    
    try:
        response = requests.request(method, url, timeout=5, **kwargs)
        
        if response.status_code >= 400:
            print(f" Erro {response.status_code}: {response.text}")
            return None
        
        return response.json()
        
    except requests.exceptions.ConnectionError:
        print(" Erro: Não foi possível conectar à API.")
        print("  Verifique se o servidor Flask está rodando.")
    except requests.exceptions.Timeout:
        print(" Erro: Tempo de resposta excedido (5 segundos).")
    except ValueError:
        print(" Erro: Resposta não está em formato JSON.")
    except Exception as e:
        print(f" Erro inesperado: {e}")
    
    return None

# ==================== FUNÇÕES AUXILIARES ====================
def print_titulo(titulo):
    """Imprime um título formatado"""
    print("\n" + "="*50)
    print(f" {titulo}")
    print("="*50)

def print_sucesso(mensagem):
    """Imprime mensagem de sucesso"""
    print(f"✅ {mensagem}")

def print_erro(mensagem):
    """Imprime mensagem de erro"""
    print(f"❌ {mensagem}")

def input_int(mensagem):
    """Pede input e converte para int com validação"""
    while True:
        try:
            return int(input(mensagem))
        except ValueError:
            print_erro("Digite um número válido!")

def input_sim_nao(mensagem):
    """Pede input de sim/não"""
    while True:
        resposta = input(f"{mensagem} (s/n): ").lower()
        if resposta in ['s', 'sim']:
            return True
        elif resposta in ['n', 'não', 'nao']:
            return False
        else:
            print_erro("Digite 's' para sim ou 'n' para não.")

# ==================== FUNÇÕES DE SETOR ====================
def criar_setor():
    print_titulo("CRIAR SETOR")
    
    nome = input("Nome do setor: ").strip()
    if not nome:
        print_erro("O nome não pode ser vazio!")
        return
    
    resposta = safe_request("POST", "/setor", json={"nome": nome})
    if resposta:
        print_sucesso(f"Setor '{nome}' criado! ID: {resposta.get('id_setor')}")

def listar_setores():
    print_titulo("LISTA DE SETORES")
    
    setores = safe_request("GET", "/setor")
    if setores is None:
        return
    
    if not setores:
        print("Nenhum setor cadastrado.")
        return
    
    for s in setores:
        print(f"  {s['id_setor']:3d} - {s['nome']}")

# ==================== FUNÇÕES DE USUÁRIO ====================
def criar_usuario():
    print_titulo("CRIAR USUÁRIO")
    
    # Listar setores primeiro
    print("Setores disponíveis:")
    setores = safe_request("GET", "/setor")
    if not setores or not setores:
        print_erro("Nenhum setor cadastrado. Crie um setor primeiro.")
        return
    
    for s in setores:
        print(f"  {s['id_setor']} - {s['nome']}")
    
    print()
    nome = input("Nome completo: ").strip()
    email = input("Email: ").strip().lower()
    setor_id = input_int("ID do setor: ")
    
    # Verificar se setor existe
    setor_existe = False
    for s in setores:
        if s['id_setor'] == setor_id:
            setor_existe = True
            break
    
    if not setor_existe:
        print_erro(f"Setor com ID {setor_id} não existe!")
        return
    
    payload = {
        "nome": nome,
        "email": email,
        "setor_id": setor_id
    }
    
    resposta = safe_request("POST", "/usuario", json=payload)
    if resposta:
        print_sucesso(f"Usuário '{nome}' criado! ID: {resposta.get('id_usuario')}")

def listar_usuarios():
    print_titulo("LISTA DE USUÁRIOS")
    
    usuarios = safe_request("GET", "/usuario")
    if usuarios is None:
        return
    
    if not usuarios:
        print("Nenhum usuário cadastrado.")
        return
    
    for u in usuarios:
        print(f"\n👤 ID: {u['id_usuario']}")
        print(f"   Nome: {u['nome']}")
        print(f"   Email: {u['email']}")
        print(f"   Setor: {u['setor']}")

# ==================== FUNÇÕES DE CHAMADO ====================
def criar_chamado():
    print_titulo("ABRIR NOVO CHAMADO")
    
    # Verificar se existem usuários
    usuarios = safe_request("GET", "/usuario")
    if not usuarios or not usuarios:
        print_erro("Nenhum usuário cadastrado. Crie um usuário primeiro.")
        return
    
    # Verificar se existem setores
    setores = safe_request("GET", "/setor")
    if not setores or not setores:
        print_erro("Nenhum setor cadastrado. Crie um setor primeiro.")
        return
    
    # Selecionar usuário
    print("Solicitantes:")
    for u in usuarios:
        print(f"  {u['id_usuario']} - {u['nome']} ({u['setor']})")
    
    usuario_id = input_int("\nID do solicitante: ")
    
    # Verificar se usuário existe
    usuario_existe = False
    for u in usuarios:
        if u['id_usuario'] == usuario_id:
            usuario_existe = True
            break
    
    if not usuario_existe:
        print_erro(f"Usuário com ID {usuario_id} não existe!")
        return
    
    # Selecionar setor
    print("\nSetores:")
    for s in setores:
        print(f"  {s['id_setor']} - {s['nome']}")
    
    setor_id = input_int("ID do setor: ")
    
    # Verificar se setor existe
    setor_existe = False
    for s in setores:
        if s['id_setor'] == setor_id:
            setor_existe = True
            break
    
    if not setor_existe:
        print_erro(f"Setor com ID {setor_id} não existe!")
        return
    
    # Dados do chamado
    print()
    titulo = input("Título do chamado: ").strip()
    descricao = input("Descrição: ").strip()
    
    print("\nPrioridades: Baixa | Média | Alta")
    prioridade = input("Prioridade: ").strip().lower()
    
    # Validar prioridade
    if prioridade not in ['baixa', 'media', 'média', 'alta']:
        print_erro("Prioridade inválida! Use: baixa, média ou alta")
        return
    
    # Normalizar prioridade
    if prioridade == 'média':
        prioridade = 'media'
    
    payload = {
        "titulo": titulo,
        "descricao": descricao,
        "usuario_id": usuario_id,
        "setor_id": setor_id,
        "prioridade": prioridade
    }
    
    resposta = safe_request("POST", "/chamados", json=payload)
    if resposta:
        print_sucesso(f"Chamado '#{resposta.get('id_chamado')}' aberto com sucesso!")
        print(f"   Status inicial: {resposta.get('status_inicial', 'aberto')}")

def listar_chamados():
    print_titulo("LISTA DE CHAMADOS")
    
    chamados = safe_request("GET", "/chamados")
    if chamados is None:
        return
    
    if not chamados:
        print("Nenhum chamado registrado.")
        return
    
    # Emojis para status e prioridade
    status_emoji = {
        'aberto': '🔴',
        'em atendimento': '🟡',
        'concluido': '🟢'
    }
    
    prioridade_emoji = {
        'alta': 'ALTA',
        'media': 'MÉDIA', 
        'baixa': 'BAIXA'
    }
    
    for c in chamados:
        emoji_status = status_emoji.get(c['status'], '⚪')
        emoji_prioridade = prioridade_emoji.get(c['prioridade'], '⚪')
        
        # Formatar data
        data = c['data_abertura']
        if 'T' in data:
            data = data.replace('T', ' ')[:19]
        
        print(f"\n{emoji_status} CHAMADO #{c['id_chamado']}")
        print(f"   {c['titulo']}")
        print(f"   {emoji_prioridade}")
        print(f"   {c['usuario']} | 🏢 {c['setor']}")
        print(f"   {data}")
        print(f"   {c['descricao'][:80]}..." if len(c['descricao']) > 80 else f"   📝 {c['descricao']}")

def atualizar_chamado():
    print_titulo("ATUALIZAR CHAMADO")
    
    chamado_id = input_int("ID do chamado: ")
    
    # Verificar se chamado existe
    resposta = safe_request("GET", "/chamados")
    if not resposta:
        return
    
    chamado_existe = False
    for c in resposta:
        if c['id_chamado'] == chamado_id:
            chamado_existe = True
            break
    
    if not chamado_existe:
        print_erro(f"Chamado #{chamado_id} não encontrado!")
        return
    
    print("\nO que deseja atualizar?")
    print("  1 - Status")
    print("  2 - Prioridade")
    print("  3 - Ambos")
    
    opcao = input("Opção (1-3): ").strip()
    
    payload = {}
    
    if opcao in ["1", "3"]:
        print("\nStatus disponíveis:")
        print("  aberto | em atendimento | concluido")
        status = input("Novo status: ").strip().lower()
        
        if status not in ['aberto', 'em atendimento', 'concluido']:
            print_erro("Status inválido!")
            return
        
        payload["status"] = status
    
    if opcao in ["2", "3"]:
        print("\nPrioridades disponíveis:")
        print("  baixa | media | alta")
        prioridade = input("Nova prioridade: ").strip().lower()
        
        if prioridade not in ['baixa', 'media', 'alta']:
            print_erro("Prioridade inválida!")
            return
        
        payload["prioridade"] = prioridade
    
    if not payload:
        print_erro("Nenhuma alteração especificada.")
        return
    
    resposta = safe_request("PUT", f"/chamados/{chamado_id}", json=payload)
    if resposta:
        print_sucesso(f"Chamado #{chamado_id} atualizado com sucesso!")

def deletar_chamado():
    print_titulo("DELETAR CHAMADO")
    
    chamado_id = input_int("ID do chamado: ")
    
    # Verificar se chamado existe
    resposta = safe_request("GET", "/chamados")
    if not resposta:
        return
    
    chamado_existe = False
    for c in resposta:
        if c['id_chamado'] == chamado_id:
            chamado_existe = True
            # Mostrar informações do chamado
            print(f"\n Título: {c['titulo']}")
            print(f"Solicitante: {c['usuario']}")
            print(f"Status: {c['status']}")
            print(f"Prioridade: {c['prioridade']}")
            break
    
    if not chamado_existe:
        print_erro(f"Chamado #{chamado_id} não encontrado!")
        return
    
    # Confirmação
    if not input_sim_nao("\nTem certeza que deseja deletar este chamado?"):
        print("Operação cancelada.")
        return
    
    resposta = safe_request("DELETE", f"/chamados/{chamado_id}")
    if resposta:
        print_sucesso(f"Chamado #{chamado_id} deletado com sucesso!")

# ==================== MENU PRINCIPAL ====================
def mostrar_menu():
    """Mostra o menu principal"""
    print_titulo("SISTEMA SERVICE DESK")
    
    opcoes = [
        ("1", "Listar setores"),
        ("2", "Criar setor"),
        ("3", "Listar usuários"),
        ("4", "Criar usuário"),
        ("5", "Listar chamados"),
        ("6", "Abrir chamado"),
        ("7", "Atualizar chamado"),
        ("8", "Deletar chamado"),
        ("0", "Sair")
    ]
    
    for codigo, descricao in opcoes:
        print(f"  {codigo} - {descricao}")
    
    print("="*50)

def verificar_api():
    """Verifica se a API está online"""
    print("🔍 Verificando conexão com a API...")
    
    resposta = safe_request("GET", "/health")
    if resposta:
        status = resposta.get('database', 'desconhecido')
        if status == 'connected':
            print_sucesso(" API conectada com sucesso!")
            print(f"   Banco de dados: {resposta.get('config', {}).get('database', 'N/A')}")
        else:
            print(" API online, mas banco de dados desconectado")
        sleep(1)
        return True
    else:
        print_erro("Não foi possível conectar à API.")
        print("\nSolução de problemas:")
        print("  1. Certifique-se de que o servidor Flask está rodando")
        print("     Comando: python app.py")
        print("  2. Verifique se o MySQL está rodando")
        print("  3. Confira se a URL está correta: http://127.0.0.1:5000")
        return False
# ==================== FUNÇÃO PRINCIPAL ====================
def main():
    """Função principal do programa"""
    print_titulo("INICIANDO SISTEMA SERVICE DESK")
    
    # Verifica API primeiro
    if not verificar_api():
        print("\nPressione Enter para sair...")
        input()
        return
    
    # Loop do menu principal
    while True:
        mostrar_menu()
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "0":
            print_titulo("SAINDO DO SISTEMA")
            print("Até logo!")
            break
        
        elif opcao == "1":
            listar_setores()
        elif opcao == "2":
            criar_setor()
        elif opcao == "3":
            listar_usuarios()
        elif opcao == "4":
            criar_usuario()
        elif opcao == "5":
            listar_chamados()
        elif opcao == "6":
            criar_chamado()
        elif opcao == "7":
            atualizar_chamado()
        elif opcao == "8":
            deletar_chamado()
        else:
            print_erro("Opção inválida! Tente novamente.")
        
        # Pausa para leitura
        input("\nPressione Enter para continuar...")

# ==================== EXECUÇÃO ====================
if __name__ == "__main__":
    try:
        main()  # ← ESTA LINHA É ESSENCIAL!!!!!!!!!!!(smp esqueco de colocar)
    except KeyboardInterrupt:
        print("\n\nPrograma interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        import traceback
        traceback.print_exc()
        input("\nPressione Enter para sair...")

    