import flet as ft
import os
import time
import threading
import csv
import json
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
ARQUIVOS_DIR = Path("arquivos")
IMAGENS_DIR = Path("imagens")
CONFIG_FILE = Path("config.json")

# Criar diretórios se não existirem
for dir_path in [LISTAS_DIR, LOG_DIR, ARQUIVOS_DIR, IMAGENS_DIR]:
    dir_path.mkdir(exist_ok=True)

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
# EXTENSÕES SUPORTADAS
# =========================
EXTENSOES_IMAGEM = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff']
EXTENSOES_VIDEO = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm']
EXTENSOES_ARQUIVO = ['.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv', '.ppt', '.pptx', '.zip', '.rar']

# =========================
# FUNÇÕES AUXILIARES
# =========================
def carregar_config():
    """Carrega configurações do arquivo JSON"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"listas_abertas": {}, "ultima_mensagem": ""}

def salvar_config(config):
    """Salva configurações no arquivo JSON"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

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
            writer.writerow(['Data', 'Hora', 'Usuario', 'Status', 'Lista', 'Mensagem', 'Arquivo'])
        writer.writerow(data)

def normalize_name(name):
    """Normaliza nomes para comparação"""
    return name.strip().lower()

def listar_arquivos_midia():
    """Lista arquivos de mídia disponíveis"""
    arquivos = []
    
    # Imagens
    for ext in EXTENSOES_IMAGEM:
        arquivos.extend(list(IMAGENS_DIR.glob(f"*{ext}")))
    
    # Vídeos
    for ext in EXTENSOES_VIDEO:
        arquivos.extend(list(IMAGENS_DIR.glob(f"*{ext}")))
    
    # Outros arquivos
    for ext in EXTENSOES_ARQUIVO:
        arquivos.extend(list(ARQUIVOS_DIR.glob(f"*{ext}")))
    
    return arquivos

# =========================
# APLICATIVO PRINCIPAL
# =========================
def main(page: ft.Page):
    # =========================
    # CONFIGURAÇÃO DA PÁGINA
    # =========================
    page.title = "Slack DM Manager Pro"
    page.window_width = 1400
    page.window_height = 900
    page.window_min_width = 1100
    page.window_min_height = 700
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = COLORS["dark_bg"]
    page.padding = 20
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
    
    config = carregar_config()
    arquivo_selecionado = None
    lista_editando = None
    
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
    
    def atualizar_lista_arquivos():
        """Atualiza a lista de arquivos de mídia"""
        arquivos_container.controls.clear()
        
        arquivos = listar_arquivos_midia()
        
        if not arquivos:
            arquivos_container.controls.append(
                ft.Text("📭 Nenhum arquivo encontrado", color=COLORS["warning"], italic=True)
            )
        else:
            for arquivo in arquivos:
                # Determinar ícone baseado na extensão
                ext = arquivo.suffix.lower()
                if ext in EXTENSOES_IMAGEM:
                    icon = "🖼️"
                elif ext in EXTENSOES_VIDEO:
                    icon = "🎬"
                else:
                    icon = "📎"
                
                # Criar botão para selecionar arquivo
                btn = ft.ElevatedButton(
                    content=ft.Row([
                        ft.Text(icon, size=16),
                        ft.Text(arquivo.name, size=12),
                    ]),
                    width=400,
                    height=35,
                    style=ft.ButtonStyle(
                        bgcolor=COLORS["card_bg"] if arquivo != arquivo_selecionado else COLORS["primary"],
                        color=COLORS["text"],
                    ),
                    on_click=lambda e, a=arquivo: selecionar_arquivo(a),
                )
                
                arquivos_container.controls.append(btn)
        
        page.update()
    
    def selecionar_arquivo(arquivo_path):
        """Seleciona um arquivo para envio"""
        nonlocal arquivo_selecionado
        arquivo_selecionado = arquivo_path
        arquivo_info.value = f"📎 Arquivo selecionado: {arquivo_path.name}"
        
        # Atualizar cores dos botões
        atualizar_lista_arquivos()
        
        log(f"Arquivo selecionado: {arquivo_path.name}", "info")
    
    def upload_arquivo(result):
        """Faz upload de um arquivo usando page.pick_files"""
        if result.files:
            for file in result.files:
                # Determinar diretório baseado na extensão
                file_path = Path(file.name)
                ext = file_path.suffix.lower()
                if ext in EXTENSOES_IMAGEM + EXTENSOES_VIDEO:
                    destino = IMAGENS_DIR / file.name
                else:
                    destino = ARQUIVOS_DIR / file.name
                
                # Evitar sobrescrever
                contador = 1
                nome_base = destino.stem
                while destino.exists():
                    destino = destino.with_name(f"{nome_base}_{contador}{destino.suffix}")
                    contador += 1
                
                try:
                    # Salvar arquivo
                    with open(destino, 'wb') as f:
                        f.write(file.read())
                    
                    log(f"✅ Arquivo enviado: {destino.name}", "success")
                except Exception as ex:
                    log(f"❌ Erro ao salvar arquivo {file.name}: {str(ex)}", "error")
            
            atualizar_lista_arquivos()
    
    def importar_lista(result):
        """Importa uma lista de arquivo usando page.pick_files"""
        if result.files:
            for file in result.files:
                if file.name.endswith('.txt'):
                    destino = LISTAS_DIR / file.name
                    
                    # Evitar sobrescrever
                    contador = 1
                    nome_base = destino.stem
                    while destino.exists():
                        destino = destino.with_name(f"{nome_base}_{contador}.txt")
                        contador += 1
                    
                    try:
                        # Salvar arquivo
                        with open(destino, 'wb') as f:
                            f.write(file.read())
                        
                        log(f"✅ Lista importada: {destino.name}", "success")
                    except Exception as ex:
                        log(f"❌ Erro ao importar lista {file.name}: {str(ex)}", "error")
            
            carregar_listas()
    
    def update_dashboard():
        dashboard_cards.controls.clear()
        
        cards_data = [
            ("📊 Total de Listas", f"{stats['total_listas']}", COLORS["primary"]),
            ("👥 Total de Usuários", f"{stats['total_usuarios']}", COLORS["success"]),
            ("📎 Arquivos", f"{len(listar_arquivos_midia())}", COLORS["secondary"]),
        ]
        
        for lista, count in stats['usuarios_por_lista'].items():
            nome_sem_ext = lista.replace('.txt', '')
            cards_data.append((f"📁 {nome_sem_ext}", f"{count} users", COLORS["warning"]))
        
        for title, value, color in cards_data:
            dashboard_cards.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(title, size=14, color=COLORS["text"], opacity=0.8),
                        ft.Text(value, size=22, weight=ft.FontWeight.BOLD, color=color),
                    ]),
                    width=180,
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
        
        arquivos_txt = list(LISTAS_DIR.glob("*.txt"))
        
        if not arquivos_txt:
            listas_container.controls.append(
                ft.Text("📭 Nenhuma lista encontrada", color=COLORS["warning"], italic=True)
            )
        else:
            for arquivo in arquivos_txt:
                try:
                    with open(arquivo, "r", encoding="utf-8") as f:
                        nomes = [normalize_name(l) for l in f if l.strip()]
                    
                    if nomes:
                        listas_data[arquivo.name] = nomes
                        
                        stats["total_listas"] += 1
                        stats["total_usuarios"] += len(nomes)
                        stats["usuarios_por_lista"][arquivo.name] = len(nomes)
                        
                        # Botão para editar lista
                        lista_btn = ft.ElevatedButton(
                            content=ft.Row([
                                ft.Text("📄", size=16),
                                ft.Text(f"{arquivo.name} ({len(nomes)} users)", size=13),
                            ]),
                            width=350,
                            height=40,
                            style=ft.ButtonStyle(
                                bgcolor=COLORS["card_bg"],
                                color=COLORS["text"],
                            ),
                            on_click=lambda e, a=arquivo: abrir_editor_lista(a),
                        )
                        
                        # Checkbox para seleção
                        checkbox = ft.Checkbox(
                            value=False,
                            on_change=lambda e, n=arquivo.name: on_checkbox_change(e, n),
                        )
                        
                        listas_checkboxes[arquivo.name] = checkbox
                        
                        listas_container.controls.append(
                            ft.Row([
                                checkbox,
                                lista_btn,
                            ], spacing=10)
                        )
                
                except Exception as e:
                    log(f"Erro ao ler {arquivo.name}: {str(e)}", "error")
        
        update_dashboard()
        log(f"Carregadas {stats['total_listas']} listas com {stats['total_usuarios']} usuários", "success")
        page.update()
    
    def on_checkbox_change(e, nome_lista):
        """Callback para mudança no checkbox"""
        # Atualizar cor do botão quando selecionado
        for control in listas_container.controls:
            if isinstance(control, ft.Row) and len(control.controls) > 1:
                checkbox, button = control.controls
                if checkbox == e.control:
                    if e.control.value:
                        button.style.bgcolor = COLORS["primary"]
                    else:
                        button.style.bgcolor = COLORS["card_bg"]
                    page.update()
                    break
    
    def abrir_editor_lista(arquivo_path):
        """Abre editor para uma lista específica"""
        nonlocal lista_editando
        lista_editando = arquivo_path
        
        try:
            with open(arquivo_path, "r", encoding="utf-8") as f:
                conteudo = f.read()
        except:
            conteudo = ""
        
        editor_conteudo.value = conteudo
        editor_titulo.value = f"Editando: {arquivo_path.name}"
        
        # Mostrar dialog
        page.dialog = editor_dialog
        editor_dialog.open = True
        page.update()
    
    def salvar_lista(e):
        """Salva a lista editada"""
        if lista_editando:
            try:
                with open(lista_editando, "w", encoding="utf-8") as f:
                    f.write(editor_conteudo.value)
                
                editor_dialog.open = False
                page.update()
                carregar_listas()
                log(f"✅ Lista salva: {lista_editando.name}", "success")
            except Exception as ex:
                log(f"❌ Erro ao salvar lista: {str(ex)}", "error")
    
    def criar_nova_lista():
        """Cria uma nova lista vazia"""
        dialog_nome.value = ""
        page.dialog = dialog_criar_lista
        dialog_criar_lista.open = True
        page.update()
    
    def confirmar_criar_lista(e):
        """Confirma criação de nova lista"""
        nome = dialog_nome.value.strip()
        if nome:
            if not nome.endswith('.txt'):
                nome += '.txt'
            
            nova_lista = LISTAS_DIR / nome
            
            # Evitar sobrescrever
            contador = 1
            nome_base = nova_lista.stem
            while nova_lista.exists():
                nova_lista = nova_lista.with_name(f"{nome_base}_{contador}.txt")
                contador += 1
            
            try:
                nova_lista.write_text("", encoding="utf-8")
                dialog_criar_lista.open = False
                page.update()
                
                # Abrir editor imediatamente
                abrir_editor_lista(nova_lista)
                log(f"✅ Lista criada: {nova_lista.name}", "success")
            except Exception as ex:
                log(f"❌ Erro ao criar lista: {str(ex)}", "error")
    
    def enviar_mensagens(e):
        """Função principal de envio de mensagens"""
        # Validar seleção
        selecionadas = [
            nome for nome, cb in listas_checkboxes.items() 
            if cb.value and nome in listas_data
        ]
        
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
        
        # Salvar mensagem atual
        config["ultima_mensagem"] = mensagem_input.value
        salvar_config(config)
        
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
                usuarios_nao_encontrados = []
                
                # Coletar todos os usuários das listas selecionadas
                usuarios_para_enviar = set()
                for lista in selecionadas:
                    if lista in listas_data:
                        usuarios_para_enviar.update(listas_data[lista])
                
                log(f"📨 Preparando {len(usuarios_para_enviar)} mensagens...", "info")
                
                if client:
                    # Modo real com Slack API
                    try:
                        usuarios_slack = client.users_list()["members"]
                        usuarios_encontrados = []
                        
                        for user in usuarios_slack:
                            if user.get("is_bot") or user.get("deleted"):
                                continue
                            
                            nome_real = user["profile"].get("real_name", "").strip()
                            nome_display = user["profile"].get("display_name", "").strip()
                            
                            nome_para_busca = nome_real or nome_display
                            if not nome_para_busca:
                                continue
                            
                            nome_normalizado = normalize_name(nome_para_busca)
                            
                            if nome_normalizado not in usuarios_para_enviar:
                                continue
                            
                            usuarios_encontrados.append(nome_normalizado)
                            
                            # Personalizar mensagem
                            texto = mensagem_input.value.replace("{{nome}}", nome_para_busca)
                            
                            try:
                                # Abrir DM
                                dm = client.conversations_open(users=user["id"])
                                
                                # Enviar mensagem com arquivo se houver
                                if arquivo_selecionado and arquivo_selecionado.exists():
                                    with open(arquivo_selecionado, 'rb') as file:
                                        response = client.files_upload_v2(
                                            channel=dm["channel"]["id"],
                                            file=file,
                                            filename=arquivo_selecionado.name,
                                            initial_comment=texto
                                        )
                                else:
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
                                    texto[:50] + "..." if len(texto) > 50 else texto,
                                    arquivo_selecionado.name if arquivo_selecionado else ""
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
                                time.sleep(2)
                        
                        # Usuários não encontrados
                        usuarios_nao_encontrados = [u for u in usuarios_para_enviar if u not in usuarios_encontrados]
                        
                    except SlackApiError as e:
                        log(f"❌ Erro geral do Slack: {e.response['error']}", "error")
                else:
                    # Modo de teste (simulação)
                    log("🔄 Modo de teste ativado (simulando envios)...", "warning")
                    
                    for i, usuario in enumerate(usuarios_para_enviar, 1):
                        texto = mensagem_input.value.replace("{{nome}}", usuario.title())
                        
                        # Log de simulação
                        log_data = [
                            datetime.now().strftime("%Y-%m-%d"),
                            datetime.now().strftime("%H:%M:%S"),
                            usuario.title(),
                            "SIMULADO",
                            selecionadas[0] if len(selecionadas) == 1 else "MULTIPLAS",
                            texto[:50] + "..." if len(texto) > 50 else texto,
                            arquivo_selecionado.name if arquivo_selecionado else ""
                        ]
                        save_to_csv(log_file, log_data)
                        
                        log(f"✅ [{i}/{len(usuarios_para_enviar)}] SIMULAÇÃO para {usuario.title()}", "success")
                        total_enviados += 1
                        
                        time.sleep(delay * 0.3)
                
                # Resumo final com usuários não encontrados
                log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "system")
                log(f"🏁 ENVIO CONCLUÍDO", "success")
                log(f"📊 Resumo:", "info")
                log(f"   • Total de mensagens: {total_enviados + total_erros}", "info")
                log(f"   • Enviadas com sucesso: {total_enviados}", "success")
                log(f"   • Erros: {total_erros}", "error" if total_erros > 0 else "info")
                
                if usuarios_nao_encontrados:
                    log(f"   • Usuários não encontrados no Slack ({len(usuarios_nao_encontrados)}):", "warning")
                    for usuario in usuarios_nao_encontrados:
                        log(f"     - {usuario.title()}", "warning")
                
                if arquivo_selecionado:
                    log(f"   • Arquivo anexado: {arquivo_selecionado.name}", "info")
                
                log(f"   • Log salvo em: {log_file.name}", "system")
                
            except Exception as ex:
                log(f"❌ Erro inesperado: {str(ex)}", "error")
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
    # Header
    header = ft.Container(
        content=ft.Row(
            [
                ft.Text("🚀", size=40, color=COLORS["primary"]),
                ft.Column([
                    ft.Text("SLACK DM MANAGER PRO", size=28, weight=ft.FontWeight.BOLD, color=COLORS["text"]),
                    ft.Text("Sistema Completo de Envio de Mensagens", size=14, color=COLORS["text"], opacity=0.8),
                ]),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "🔄 Atualizar",
                    on_click=lambda e: (carregar_listas(), atualizar_lista_arquivos()),
                    height=40,
                )
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=20
    )
    
    # Dashboard
    dashboard_cards = ft.Row(spacing=15, wrap=True)
    
    # Listas container
    listas_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=250)
    
    # Controles de envio
    mensagem_input = ft.TextField(
        label="Digite sua mensagem",
        multiline=True,
        min_lines=8,
        hint_text="Olá {{nome}}, como você está?\n\nUse {{nome}} para personalizar a mensagem.",
        border_color=COLORS["primary"],
        focused_border_color=COLORS["secondary"],
        expand=True,
        value=config.get("ultima_mensagem", "")
    )
    
    delay_input = ft.Slider(
        min=1,
        max=5,
        divisions=40,
        label="{value}s",
        value=1.5,
        active_color=COLORS["primary"],
        inactive_color=COLORS["card_bg"],
        width=300,
    )
    
    delay_info = ft.Text("Delay entre mensagens: 1.5s", size=12, color=COLORS["text"], opacity=0.7)
    
    def on_delay_change(e):
        delay_info.value = f"Delay entre mensagens: {delay_input.value:.1f}s"
        page.update()
    
    delay_input.on_change = on_delay_change
    
    # Área de log
    log_area = ft.ListView(spacing=5, padding=10, auto_scroll=True, expand=True)
    
    # Contêiner de arquivos
    arquivos_container = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO, height=150)
    arquivo_info = ft.Text("📎 Nenhum arquivo selecionado", size=12, color=COLORS["text"], opacity=0.8)
    
    # Botões
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
    
    # Diálogos
    editor_conteudo = ft.TextField(multiline=True, min_lines=20, expand=True)
    editor_titulo = ft.Text(size=16, weight=ft.FontWeight.BOLD)
    
    editor_dialog = ft.AlertDialog(
        modal=True,
        title=editor_titulo,
        content=ft.Container(
            content=editor_conteudo,
            width=600,
            height=400,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: setattr(editor_dialog, 'open', False)),
            ft.ElevatedButton("Salvar", on_click=salvar_lista, bgcolor=COLORS["success"]),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    dialog_nome = ft.TextField(label="Nome da lista", hint_text="ex: lista_clientes.txt")
    dialog_criar_lista = ft.AlertDialog(
        modal=True,
        title=ft.Text("Criar Nova Lista"),
        content=dialog_nome,
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: setattr(dialog_criar_lista, 'open', False)),
            ft.ElevatedButton("Criar", on_click=confirmar_criar_lista, bgcolor=COLORS["success"]),
        ],
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
                        # Coluna esquerda (listas, arquivos e controles)
                        ft.Container(
                            width=500,
                            content=ft.Column(
                                [
                                    # Listas
                                    ft.Row([
                                        ft.Text("📋 LISTAS DISPONÍVEIS", size=16, weight=ft.FontWeight.BOLD),
                                        ft.OutlinedButton("➕ Criar", on_click=lambda e: criar_nova_lista()),
                                        ft.OutlinedButton("📥 Importar", on_click=lambda e: page.pick_files(
                                            allowed_extensions=['txt'],
                                            allow_multiple=True,
                                            on_result=importar_lista
                                        )),
                                    ]),
                                    ft.Container(
                                        content=listas_container,
                                        border=ft.border.all(1, COLORS["card_bg"]),
                                        border_radius=10,
                                        padding=15,
                                    ),
                                    
                                    ft.Divider(height=20),
                                    
                                    # Arquivos
                                    ft.Text("📎 ARQUIVOS E MÍDIA", size=16, weight=ft.FontWeight.BOLD),
                                    arquivo_info,
                                    ft.Row([
                                        ft.ElevatedButton(
                                            "📤 Upload Arquivo",
                                            on_click=lambda e: page.pick_files(
                                                allow_multiple=True,
                                                on_result=upload_arquivo
                                            ),
                                        ),
                                        ft.OutlinedButton("🔄 Atualizar", on_click=lambda e: atualizar_lista_arquivos()),
                                    ]),
                                    ft.Container(
                                        content=arquivos_container,
                                        border=ft.border.all(1, COLORS["card_bg"]),
                                        border_radius=10,
                                        padding=10,
                                    ),
                                    
                                    ft.Divider(height=20),
                                    
                                    # Configurações
                                    ft.Text("⚙️ CONFIGURAÇÕES", size=16, weight=ft.FontWeight.BOLD),
                                    delay_info,
                                    ft.Row([delay_input], width=300),
                                    
                                    ft.Divider(height=20),
                                    
                                    # Botões de ação
                                    ft.Column([
                                        enviar_btn,
                                        ft.Container(height=10),
                                        ft.Row([
                                            limpar_log_btn,
                                            ft.Container(expand=True),
                                            ft.Text(f"v1.3.0", size=10, color=COLORS["text"], opacity=0.5),
                                        ]),
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
    
    # Atualizar página
    page.update()
    
    # Carregar dados iniciais
    carregar_listas()
    atualizar_lista_arquivos()

# =========================
# INICIAR APLICATIVO
# =========================
if __name__ == "__main__":
    print("🚀 Iniciando Slack DM Manager Pro v1.3.0...")
    print(f"📁 Diretório de listas: {LISTAS_DIR.absolute()}")
    print(f"📁 Diretório de logs: {LOG_DIR.absolute()}")
    print(f"📁 Diretório de imagens: {IMAGENS_DIR.absolute()}")
    print(f"📁 Diretório de arquivos: {ARQUIVOS_DIR.absolute()}")
    
    print("\n📱 Iniciando interface gráfica...")
    
    # Iniciar aplicativo
    ft.run(main)