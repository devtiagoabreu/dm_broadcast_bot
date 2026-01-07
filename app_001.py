import flet as ft
import os
import time
import threading
import csv
from datetime import datetime
from pathlib import Path
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# =========================
# CONFIGURAÇÃO
# =========================
LISTAS_DIR = Path("listas")
LOG_DIR = Path("logs")
LISTAS_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

load_dotenv()
SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")

if SLACK_TOKEN:
    client = WebClient(token=SLACK_TOKEN)
else:
    client = None
    print("⚠️ Token Slack não encontrado. Modo de teste ativado.")

# =========================
# CORES E TEMA
# =========================
COLORS = {
    "primary": "#4A90E2",
    "secondary": "#7B61FF",
    "success": "#50C878",
    "warning": "#FFA500",
    "danger": "#FF6B6B",
    "dark_bg": "#0F172A",
    "card_bg": "#1E293B",
    "text": "#F1F5F9"
}

# =========================
# FUNÇÕES AUXILIARES
# =========================
def create_log_csv():
    """Cria arquivo CSV para logs"""
    log_file = LOG_DIR / f"log_envio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return log_file

def save_to_csv(log_file, data):
    """Salva dados no CSV de log"""
    file_exists = log_file.exists()
    
    with open(log_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Data', 'Hora', 'Usuario', 'Status', 'Lista', 'Mensagem'])
        writer.writerow(data)

def normalize_name(name):
    """Normaliza nomes para comparação"""
    return name.strip().lower()

# =========================
# APLICATIVO PRINCIPAL
# =========================
def main(page: ft.Page):
    # =========================
    # CONFIGURAÇÃO DA PÁGINA
    # =========================
    page.title = "Slack DM Manager Pro"
    page.window_width = 1300
    page.window_height = 850
    page.window_min_width = 1000
    page.window_min_height = 700
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = COLORS["dark_bg"]
    page.padding = 25
    page.scroll = ft.ScrollMode.AUTO
    
    # =========================
    # VARIÁVEIS DO APLICATIVO
    # =========================
    listas_data = {}
    listas_checkboxes = {}
    stats = {
        "total_listas": 0,
        "total_usuarios": 0,
        "usuarios_por_lista": {}
    }
    
    # =========================
    # FUNÇÕES DO APLICATIVO
    # =========================
    def log(msg, tipo="info"):
        """Adiciona entrada ao log com cores"""
        colors = {
            "info": COLORS["text"],
            "success": COLORS["success"],
            "warning": COLORS["warning"],
            "error": COLORS["danger"],
            "system": COLORS["primary"]
        }
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Adicionar emoji baseado no tipo
        emoji = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "system": "🔧"
        }.get(tipo, "ℹ️")
        
        log_entry = ft.Row([
            ft.Text(f"[{timestamp}] ", size=12, color=colors["system"], weight=ft.FontWeight.BOLD),
            ft.Text(f"{emoji} ", size=13),
            ft.Text(msg, size=13, color=colors.get(tipo, COLORS["text"])),
        ], tight=True)
        
        log_area.controls.append(log_entry)
        page.update()
    
    def limpar_log():
        log_area.controls.clear()
        log("Log limpo", "system")
        page.update()
    
    def update_dashboard():
        dashboard_cards.controls.clear()
        
        cards_data = [
            ("📊 Total de Listas", f"{stats['total_listas']}", COLORS["primary"]),
            ("👥 Total de Usuários", f"{stats['total_usuarios']}", COLORS["success"]),
            ("⚡ Status", "Pronto" if client else "Modo Teste", COLORS["warning"] if client else COLORS["danger"]),
        ]
        
        # Adicionar cards para cada lista
        for lista, count in stats['usuarios_por_lista'].items():
            nome_sem_ext = lista.replace('.txt', '')
            cards_data.append((f"📁 {nome_sem_ext}", f"{count} users", COLORS["secondary"]))
        
        for title, value, color in cards_data:
            dashboard_cards.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(title, size=14, color=COLORS["text"], opacity=0.8),
                        ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=color),
                    ]),
                    width=200,
                    padding=15,
                    bgcolor=COLORS["card_bg"],
                    border_radius=10,
                )
            )
        
        page.update()
    
    def carregar_listas():
        """Carrega listas do diretório"""
        listas_data.clear()
        listas_checkboxes.clear()
        listas_container.controls.clear()
        
        stats["total_listas"] = 0
        stats["total_usuarios"] = 0
        stats["usuarios_por_lista"].clear()
        
        # Listar TODOS os arquivos .txt, não apenas lista_*.txt
        arquivos_txt = list(LISTAS_DIR.glob("*.txt"))
        
        # Mostrar quais arquivos estão sendo encontrados
        print(f"Arquivos encontrados na pasta 'listas': {[f.name for f in arquivos_txt]}")
        
        if not arquivos_txt:
            log("Nenhum arquivo .txt encontrado na pasta 'listas'", "warning")
            listas_container.controls.append(
                ft.Text("📭 Nenhum arquivo .txt encontrado na pasta 'listas'", 
                       color=COLORS["warning"], italic=True)
            )
        else:
            for arquivo in arquivos_txt:
                try:
                    with open(arquivo, "r", encoding="utf-8") as f:
                        # Ler todas as linhas e remover espaços em branco
                        linhas = [l.strip() for l in f.readlines()]
                        nomes = [normalize_name(l) for l in linhas if l]
                    
                    print(f"Arquivo: {arquivo.name}, Linhas lidas: {len(linhas)}, Nomes válidos: {len(nomes)}")
                    
                    if nomes:
                        listas_data[arquivo.name] = nomes
                        
                        # Atualizar estatísticas
                        stats["total_listas"] += 1
                        stats["total_usuarios"] += len(nomes)
                        stats["usuarios_por_lista"][arquivo.name] = len(nomes)
                        
                        # Criar checkbox
                        checkbox = ft.Checkbox(
                            label=f"📄 {arquivo.name} ({len(nomes)} usuários)",
                            value=False,
                            fill_color=COLORS["primary"],
                        )
                        listas_checkboxes[arquivo.name] = checkbox
                        
                        listas_container.controls.append(checkbox)
                        
                        # Mostrar no console os nomes lidos (após normalização)
                        print(f"Nomes em {arquivo.name}: {nomes}")
                    else:
                        print(f"⚠️ Arquivo {arquivo.name} está vazio ou tem apenas linhas em branco")
                
                except Exception as e:
                    error_msg = f"Erro ao ler {arquivo.name}: {str(e)}"
                    print(f"❌ {error_msg}")
                    log(error_msg, "error")
        
        update_dashboard()
        log(f"Carregadas {stats['total_listas']} listas com {stats['total_usuarios']} usuários", "success")
        page.update()
    
    def criar_nova_lista():
        """Cria uma nova lista vazia"""
        from datetime import datetime
        
        # Usar timestamp para nome único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nova_lista = LISTAS_DIR / f"lista_{timestamp}.txt"
        nova_lista.write_text("# Adicione nomes aqui, um por linha\n# Exemplo: João Silva\n", encoding="utf-8")
        
        log(f"Lista criada: {nova_lista.name}", "success")
        carregar_listas()
    
    def enviar_mensagens(e):
        """Função principal de envio de mensagens"""
        # Validar seleção
        selecionadas = [
            nome for nome, cb in listas_checkboxes.items() 
            if cb.value and nome in listas_data
        ]
        
        print(f"Listas selecionadas: {selecionadas}")
        
        if not selecionadas:
            log("❌ Selecione pelo menos uma lista", "error")
            return
        
        if not mensagem_input.value.strip():
            log("❌ Digite uma mensagem", "error")
            return
        
        # Validar delay
        try:
            delay = float(delay_input.value)
        except ValueError:
            log("❌ Valor de delay inválido", "error")
            return
        
        if delay < 1.0:
            log("⚠️ Delay muito baixo. Mínimo recomendado: 1.0s", "warning")
            return
        
        # Criar arquivo de log
        log_file = create_log_csv()
        log(f"📁 Log será salvo em: {log_file.name}", "system")
        
        # Desabilitar botão durante envio
        enviar_btn.disabled = True
        enviar_btn.content = ft.Row([
            ft.Text("⏳", size=20),
            ft.Text("ENVIANDO...", weight=ft.FontWeight.BOLD),
        ])
        enviar_btn.bgcolor = COLORS["warning"]
        page.update()
        
        def worker():
            try:
                log(f"🚀 Iniciando envio para {len(selecionadas)} lista(s)...", "success")
                log(f"⏱️  Delay entre mensagens: {delay}s", "info")
                log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "system")
                
                total_enviados = 0
                total_erros = 0
                
                # Coletar todos os usuários das listas selecionadas
                usuarios_para_enviar = set()
                for lista in selecionadas:
                    if lista in listas_data:
                        usuarios_para_enviar.update(listas_data[lista])
                
                print(f"Usuários para enviar: {usuarios_para_enviar}")
                log(f"📨 Preparando {len(usuarios_para_enviar)} mensagens...", "info")
                
                if client:
                    # Modo real com Slack API
                    try:
                        usuarios_slack = client.users_list()["members"]
                        print(f"Total de usuários no Slack: {len(usuarios_slack)}")
                        
                        for user in usuarios_slack:
                            if user.get("is_bot") or user.get("deleted"):
                                continue
                            
                            nome_real = user["profile"].get("real_name", "").strip()
                            nome_display = user["profile"].get("display_name", "").strip()
                            
                            # Tentar ambos os nomes
                            nome_para_busca = nome_real or nome_display
                            if not nome_para_busca:
                                continue
                            
                            nome_normalizado = normalize_name(nome_para_busca)
                            
                            # Debug: mostrar comparação
                            if nome_normalizado in usuarios_para_enviar:
                                print(f"✅ Encontrado: {nome_para_busca} -> {nome_normalizado}")
                            else:
                                # Verificar se há correspondência parcial
                                for usuario_lista in usuarios_para_enviar:
                                    if usuario_lista in nome_normalizado or nome_normalizado in usuario_lista:
                                        print(f"⚠️ Correspondência parcial: {usuario_lista} <-> {nome_normalizado}")
                            
                            if nome_normalizado not in usuarios_para_enviar:
                                continue
                            
                            # Personalizar mensagem
                            texto = mensagem_input.value.replace("{{nome}}", nome_para_busca)
                            
                            try:
                                # Abrir DM
                                dm = client.conversations_open(users=user["id"])
                                # Enviar mensagem
                                client.chat_postMessage(
                                    channel=dm["channel"]["id"],
                                    text=texto
                                )
                                
                                # Log e CSV
                                log_data = [
                                    datetime.now().strftime("%Y-%m-%d"),
                                    datetime.now().strftime("%H:%M:%S"),
                                    nome_para_busca,
                                    "ENVIADO",
                                    selecionadas[0] if len(selecionadas) == 1 else "MULTIPLAS",
                                    texto[:50] + "..." if len(texto) > 50 else texto
                                ]
                                save_to_csv(log_file, log_data)
                                
                                log(f"✅ Enviado para {nome_para_busca}", "success")
                                total_enviados += 1
                                
                                # Delay anti-ban
                                time.sleep(delay)
                                
                            except SlackApiError as api_error:
                                error_msg = api_error.response.get('error', 'Erro desconhecido')
                                log(f"❌ Erro para {nome_para_busca}: {error_msg}", "error")
                                total_erros += 1
                                time.sleep(2)  # Delay maior em caso de erro
                        
                    except SlackApiError as e:
                        log(f"❌ Erro geral do Slack: {e.response['error']}", "error")
                else:
                    # Modo de teste (simulação) - MUITO MAIS VERBOSO
                    log("🔄 Modo de teste ativado (simulando envios)...", "warning")
                    log(f"📝 Listas selecionadas: {', '.join(selecionadas)}", "info")
                    log(f"👤 Usuários encontrados: {', '.join([u.title() for u in usuarios_para_enviar])}", "info")
                    
                    for i, usuario in enumerate(usuarios_para_enviar, 1):
                        texto = mensagem_input.value.replace("{{nome}}", usuario.title())
                        
                        # Log de simulação
                        log_data = [
                            datetime.now().strftime("%Y-%m-%d"),
                            datetime.now().strftime("%H:%M:%S"),
                            usuario.title(),
                            "SIMULADO",
                            selecionadas[0] if len(selecionadas) == 1 else "MULTIPLAS",
                            texto[:50] + "..." if len(texto) > 50 else texto
                        ]
                        save_to_csv(log_file, log_data)
                        
                        log(f"✅ [{i}/{len(usuarios_para_enviar)}] SIMULAÇÃO para {usuario.title()}", "success")
                        total_enviados += 1
                        
                        # Mostrar mensagem sendo enviada
                        log(f"   📝 Mensagem: {texto[:100]}...", "info")
                        
                        time.sleep(delay * 0.3)  # Delay menor em modo simulação
                
                # Resumo final
                log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "system")
                log(f"🏁 ENVIO CONCLUÍDO", "success")
                log(f"📊 Resumo:", "info")
                log(f"   • Total de mensagens: {total_enviados + total_erros}", "info")
                log(f"   • Enviadas com sucesso: {total_enviados}", "success")
                log(f"   • Erros: {total_erros}", "error" if total_erros > 0 else "info")
                log(f"   • Log salvo em: {log_file.name}", "system")
                
            except Exception as ex:
                log(f"❌ Erro inesperado: {str(ex)}", "error")
                import traceback
                log(f"❌ Traceback: {traceback.format_exc()}", "error")
            finally:
                # Reabilitar botão
                enviar_btn.disabled = False
                enviar_btn.content = ft.Row([
                    ft.Text("📤", size=20),
                    ft.Text("INICIAR ENVIO", weight=ft.FontWeight.BOLD),
                ])
                enviar_btn.bgcolor = COLORS["success"]
                page.update()
        
        # Executar em thread separada
        threading.Thread(target=worker, daemon=True).start()
    
    # =========================
    # COMPONENTES DA UI
    # =========================
    # Header com logo
    header = ft.Container(
        content=ft.Row(
            [
                ft.Text("🚀", size=40, color=COLORS["primary"]),
                ft.Column([
                    ft.Text("SLACK DM MANAGER PRO", size=28, weight=ft.FontWeight.BOLD, color=COLORS["text"]),
                    ft.Text("Sistema de Envio de Mensagens Diretas", size=14, color=COLORS["text"], opacity=0.8),
                ]),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "🔄",
                    on_click=lambda e: carregar_listas(),
                    tooltip="Atualizar listas",
                    width=50,
                    height=50,
                    style=ft.ButtonStyle(
                        bgcolor=COLORS["card_bg"],
                        shape=ft.RoundedRectangleBorder(radius=8),
                    )
                )
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.only(bottom=20)
    )
    
    # Dashboard de estatísticas
    dashboard_cards = ft.Row(
        spacing=20,
        wrap=True,
    )
    
    # Área de seleção de listas
    listas_container = ft.Column(
        spacing=15,
        scroll=ft.ScrollMode.AUTO,
        height=300,
    )
    
    # Controles de envio
    mensagem_input = ft.TextField(
        label="Digite sua mensagem",
        multiline=True,
        min_lines=6,
        hint_text="Olá {{nome}}, como você está?\n\nUse {{nome}} para personalizar a mensagem para cada usuário.",
        border_color=COLORS["primary"],
        focused_border_color=COLORS["secondary"],
        expand=True,
        value="Olá {{nome}}, tudo bem? Espero que esteja tendo um ótimo dia! 😊"
    )
    
    delay_input = ft.Slider(
        min=1,
        max=5,
        divisions=40,
        label="{value}s",
        value=1.5,
        active_color=COLORS["primary"],
        inactive_color=COLORS["card_bg"],
    )
    
    delay_info = ft.Text("Delay entre mensagens: 1.5s (recomendado: 1.2-2s)", size=12, color=COLORS["text"], opacity=0.7)
    
    def on_delay_change(e):
        delay_info.value = f"Delay entre mensagens: {delay_input.value:.1f}s (recomendado: 1.2-2s)"
        page.update()
    
    delay_input.on_change = on_delay_change
    
    # Área de log
    log_area = ft.ListView(
        spacing=5,
        padding=10,
        auto_scroll=True,
        expand=True,
    )
    
    # Botões de ação
    enviar_btn = ft.ElevatedButton(
        content=ft.Row([
            ft.Text("📤", size=20),
            ft.Text("INICIAR ENVIO", weight=ft.FontWeight.BOLD),
        ]),
        style=ft.ButtonStyle(
            bgcolor=COLORS["success"],
            color="white",
            padding=15,
        ),
        on_click=enviar_mensagens,
    )
    
    limpar_log_btn = ft.OutlinedButton(
        content=ft.Row([
            ft.Text("🗑️", size=16),
            ft.Text("Limpar Log"),
        ]),
        on_click=lambda e: limpar_log(),
    )
    
    criar_lista_btn = ft.OutlinedButton(
        content=ft.Row([
            ft.Text("➕", size=16),
            ft.Text("Criar Nova Lista"),
        ]),
        on_click=lambda e: criar_nova_lista(),
    )
    
    # =========================
    # LAYOUT PRINCIPAL
    # =========================
    page.add(
        ft.Column(
            [
                header,
                
                # Dashboard
                ft.Text("📊 DASHBOARD", size=18, weight=ft.FontWeight.BOLD, color=COLORS["text"]),
                dashboard_cards,
                
                ft.Divider(height=20, color=COLORS["card_bg"]),
                
                # Corpo principal
                ft.Row(
                    [
                        # Coluna esquerda (listas e controles)
                        ft.Container(
                            width=450,
                            content=ft.Column(
                                [
                                    ft.Row([
                                        ft.Text("📋 LISTAS DISPONÍVEIS", size=16, weight=ft.FontWeight.BOLD),
                                        criar_lista_btn,
                                    ]),
                                    ft.Container(
                                        content=listas_container,
                                        border=ft.border.all(1, COLORS["card_bg"]),
                                        border_radius=10,
                                        padding=15,
                                    ),
                                    
                                    ft.Divider(height=20),
                                    
                                    ft.Text("⚙️ CONFIGURAÇÕES", size=16, weight=ft.FontWeight.BOLD),
                                    delay_info,
                                    delay_input,
                                    
                                    ft.Divider(height=20),
                                    
                                    ft.Column([
                                        enviar_btn,
                                        ft.Container(height=10),
                                        limpar_log_btn,
                                    ], spacing=0),
                                ],
                                spacing=15,
                            ),
                        ),
                        
                        # Divider vertical
                        ft.VerticalDivider(width=1, color=COLORS["card_bg"]),
                        
                        # Coluna direita (mensagem e logs)
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("✉️ MENSAGEM", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Container(
                                        content=mensagem_input,
                                        border=ft.border.all(1, COLORS["card_bg"]),
                                        border_radius=10,
                                        padding=15,
                                    ),
                                    
                                    ft.Divider(height=20),
                                    
                                    ft.Row([
                                        ft.Text("📜 LOG DE EXECUÇÃO", size=16, weight=ft.FontWeight.BOLD),
                                        ft.Text("(em tempo real)", size=12, color=COLORS["text"], opacity=0.7),
                                    ]),
                                    ft.Container(
                                        content=log_area,
                                        border=ft.border.all(1, COLORS["card_bg"]),
                                        border_radius=10,
                                        padding=15,
                                        expand=True,
                                    ),
                                ],
                                spacing=15,
                                expand=True,
                            ),
                            expand=True,
                        ),
                    ],
                    spacing=25,
                    expand=True,
                ),
            ],
            spacing=20,
            expand=True,
        )
    )
    
    # Carregar listas ao iniciar
    carregar_listas()

# =========================
# INICIAR APLICATIVO
# =========================
if __name__ == "__main__":
    print("🚀 Iniciando Slack DM Manager Pro...")
    print(f"📁 Diretório de listas: {LISTAS_DIR.absolute()}")
    print(f"📁 Diretório de logs: {LOG_DIR.absolute()}")
    
    # Verificar conteúdo das listas
    print("\n🔍 Verificando conteúdo das listas...")
    
    if not any(LISTAS_DIR.glob("*.txt")):
        print("⚠️  Nenhum arquivo .txt encontrado. Criando exemplos...")
        LISTAS_DIR.mkdir(exist_ok=True)
        
        exemplo_marketing = LISTAS_DIR / "lista_a.txt"
        exemplo_marketing.write_text("""João Silva
Maria Santos
Pedro Oliveira""", encoding="utf-8")
        
        exemplo_vendas = LISTAS_DIR / "lista_b.txt"
        exemplo_vendas.write_text("""Ana Costa
Carlos Rodrigues
Fernanda Lima""", encoding="utf-8")
        
        print(f"✅ Criadas listas de exemplo:")
        print(f"   - {exemplo_marketing.name}")
        print(f"   - {exemplo_vendas.name}")
    else:
        # Mostrar conteúdo das listas existentes
        for arquivo in LISTAS_DIR.glob("*.txt"):
            print(f"\n📄 Conteúdo de {arquivo.name}:")
            try:
                with open(arquivo, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                    print(f"--- INÍCIO ---")
                    print(conteudo)
                    print(f"--- FIM ---")
                    print(f"Linhas: {len(conteudo.splitlines())}")
                    print(f"Caracteres: {len(conteudo)}")
            except Exception as e:
                print(f"❌ Erro ao ler {arquivo.name}: {e}")
    
    print("\n📱 Iniciando interface gráfica...")
    
    # Iniciar aplicativo
    ft.app(target=main)