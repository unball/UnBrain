import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
# pyrefly: ignore [missing-import]
from tools.ai_training_worker import AITrainingWorker

# For Matplotlib in GTK3
import matplotlib
matplotlib.use('GTK3Agg')
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class AITrainingView(Gtk.Box):
    def __init__(self, controller, world, mainStack):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_border_width(10)

        mainStack.add_titled(self, "aiTraining", "AI Training")

        self.controller = controller
        self.world = world
        self.worker = AITrainingWorker()
        self.timeout_id = None

        # Caixa lateral com as opções desta aba: substitui o sidePanelBox
        # padrão (via leftPanelStack) enquanto "AI Training" estiver visível,
        # ligado em main_system/view/__init__.py.
        self.options_scrolled = Gtk.ScrolledWindow()
        self.options_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.options_scrolled.set_propagate_natural_width(False)
        self.options_scrolled.set_propagate_natural_height(False)
        self.options_scrolled.set_min_content_height(100)
        self.options_scrolled.show()

        self.options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.options_box.set_border_width(10)
        self.options_box.set_size_request(150, -1)
        self.options_scrolled.add_with_viewport(self.options_box)

        lbl_options = Gtk.Label()
        lbl_options.set_markup("<b>Opções AI Training</b>")
        lbl_options.set_margin_bottom(5)
        self.options_box.pack_start(lbl_options, False, False, 0)

        # Title
        lbl_title = Gtk.Label()
        lbl_title.set_markup("<span size='x-large' weight='bold'>AI Training (EWC + Sim-to-Real)</span>")
        self.pack_start(lbl_title, False, False, 10)

        # Config options
        self.chk_vision_noise = Gtk.CheckButton(label="Vision Noise (Domain Randomization)")
        self.chk_vision_noise.set_active(False)
        self.options_box.pack_start(self.chk_vision_noise, False, False, 0)

        self.chk_apply_delay = Gtk.CheckButton(label="Vision/Network Delay")
        self.chk_apply_delay.set_active(True)
        self.chk_apply_delay.set_tooltip_text(
            "Delay de visão em modo SEM curriculum (stage fixo 4).\n"
            "Com curriculum, use os botões 'Curriculum (com/sem delay)'.")
        self.options_box.pack_start(self.chk_apply_delay, False, False, 0)

        self.chk_allies = Gtk.CheckButton(label="Train AI + Classic Entities (3 Robots)")
        self.chk_allies.set_active(False)
        self.options_box.pack_start(self.chk_allies, False, False, 0)

        self.chk_render_hlc = Gtk.CheckButton(label="Draw HLC (Render rSoccer Field)")
        self.chk_render_hlc.set_active(False)
        self.chk_render_hlc.connect("toggled", self.on_chk_render_hlc_toggled)
        self.options_box.pack_start(self.chk_render_hlc, False, False, 0)

        # Curriculum Learning: desligado por padrão para testes limpos (stage fixo 4).
        # Os dois botões ligam o curriculum completo, com ou sem delay de visão.
        lbl_curr = Gtk.Label()
        lbl_curr.set_markup("<b>Curriculum Learning</b>")
        lbl_curr.set_margin_top(10)
        lbl_curr.set_halign(Gtk.Align.START)
        self.options_box.pack_start(lbl_curr, False, False, 0)

        self.radio_curr_off = Gtk.RadioButton.new_with_label_from_widget(None, "Desligado (stage 4 direto)")
        self.radio_curr_off.set_active(True)
        self.options_box.pack_start(self.radio_curr_off, False, False, 0)

        self.radio_curr_no_delay = Gtk.RadioButton.new_with_label_from_widget(
            self.radio_curr_off, "Curriculum (sem delay)")
        self.options_box.pack_start(self.radio_curr_no_delay, False, False, 0)

        self.radio_curr_delay = Gtk.RadioButton.new_with_label_from_widget(
            self.radio_curr_off, "Curriculum (com delay)")
        self.radio_curr_delay.set_tooltip_text(
            "Delay por stage: 0 (stages 1-2), 1 frame (stage 3), aleatório U[1..5] (stage 4).\n"
            "Se 'Delay frames' for preenchido, o valor fixo entra a partir do stage 4.")
        self.options_box.pack_start(self.radio_curr_delay, False, False, 0)

        hbox_delay_frames = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        lbl_delay_frames = Gtk.Label(label="Delay frames:")
        hbox_delay_frames.pack_start(lbl_delay_frames, False, False, 0)

        self.entry_delay_frames = Gtk.Entry()
        self.entry_delay_frames.set_width_chars(6)
        self.entry_delay_frames.set_placeholder_text("vazio = U[1..5]")
        self.entry_delay_frames.set_tooltip_text(
            "Nº de frames de delay (1 frame = 25ms). Vazio = aleatório U[1..5] por episódio.\n"
            "Valor manual só é aplicado a partir do stage 4.")
        hbox_delay_frames.pack_start(self.entry_delay_frames, True, True, 0)
        self.options_box.pack_start(hbox_delay_frames, False, False, 0)

        self.chk_anneal_shaping = Gtk.CheckButton(label="Anneal Shaping (stage 4)")
        self.chk_anneal_shaping.set_active(False)
        self.chk_anneal_shaping.set_tooltip_text(
            "Anneal v2 (stage 4): encolhe o shaping inteiro ×0.3 — positivos\n"
            "(move, shot_on_goal) E penalidades (lost_ball, wall, ball_wall) —\n"
            "e amplia o gol ×2.5 (+50/−25). Objetivo: gol dominar o gradiente\n"
            "(antes o shaping era ~30× o gol). Energy fica intacta.\n"
            "Atenção: muda a escala do avg_return (plots ficam incomparáveis).")
        self.options_box.pack_start(self.chk_anneal_shaping, False, False, 0)

        self.chk_augment_obs = Gtk.CheckButton(label="Obs + ações (delay)")
        self.chk_augment_obs.set_active(False)
        self.chk_augment_obs.set_tooltip_text(
            "Aumenta o observador de estado: anexa à observação as últimas ações não-observadas\n"
            "+ indicador de delay (40 -> 40+2Δ+1 dims) — restaura a propriedade de\n"
            "Markov sob delay. EXIGE modelo com entrada expandida: use\n"
            "expand_obs_checkpoint.py para migrar um modelo 40-dim sem perda,\n"
            "ou treine do zero. Modelos antigos: deixe OFF.")
        self.options_box.pack_start(self.chk_augment_obs, False, False, 0)

        self.chk_pbrs_move = Gtk.CheckButton(label="Move PBRS")
        self.chk_pbrs_move.set_active(False)
        self.chk_pbrs_move.set_tooltip_text(
            "Troca o move por diferença de potencial (PBRS, Ng et al. 1999):\n"
            "recompensa a REDUÇÃO de distância ao alvo em vez de velocidade na\n"
            "direção — a soma telescopa (orbitar rende ~0), eliminando o farming\n"
            "sem mudar a política ótima. Muda a composição do avg_return.")
        self.options_box.pack_start(self.chk_pbrs_move, False, False, 0)

        # Self-Play config
        lbl_sp = Gtk.Label()
        lbl_sp.set_markup("<b>Self-Play / EWC</b>")
        lbl_sp.set_margin_top(10)
        lbl_sp.set_halign(Gtk.Align.START)
        self.options_box.pack_start(lbl_sp, False, False, 0)

        self.chk_self_play = Gtk.CheckButton(label="Enable 1v1 Self-Play")
        self.chk_self_play.set_active(True)
        self.options_box.pack_start(self.chk_self_play, False, False, 0)

        self.chk_self_play_1v2 = Gtk.CheckButton(label="Self Play 1v2")
        self.chk_self_play_1v2.set_active(False)
        self.options_box.pack_start(self.chk_self_play_1v2, False, False, 0)

        hbox_sp_interval = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        lbl_sp_interval = Gtk.Label(label="Save Interval:")
        hbox_sp_interval.pack_start(lbl_sp_interval, False, False, 0)

        self.entry_self_play_interval = Gtk.Entry()
        self.entry_self_play_interval.set_text("10")
        self.entry_self_play_interval.set_width_chars(5)
        hbox_sp_interval.pack_start(self.entry_self_play_interval, True, True, 0)
        self.options_box.pack_start(hbox_sp_interval, False, False, 0)

        hbox_ewc = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        lbl_ewc = Gtk.Label(label="EWC λ:")
        hbox_ewc.pack_start(lbl_ewc, False, False, 0)

        self.entry_ewc_lambda = Gtk.Entry()
        self.entry_ewc_lambda.set_width_chars(7)
        self.entry_ewc_lambda.set_placeholder_text("do ckpt")
        self.entry_ewc_lambda.set_tooltip_text(
            "Peso da âncora EWC. Vazio = usa o do checkpoint (2000).\n"
            "λ=2000 travou a adaptação ao reward novo (política congelada 26M steps);\n"
            "para sessões de ADAPTAÇÃO use ~10-50, ou marque Reset EWC.")
        hbox_ewc.pack_start(self.entry_ewc_lambda, True, True, 0)
        self.options_box.pack_start(hbox_ewc, False, False, 0)

        self.chk_reset_ewc = Gtk.CheckButton(label="Reset EWC anchor")
        self.chk_reset_ewc.set_active(False)
        self.chk_reset_ewc.set_tooltip_text(
            "Descarta fisher/means do checkpoint: a sessão treina livre da âncora\n"
            "antiga e a próxima consolidação re-ancora na política nova.\n"
            "Seguro: o modelo base continua salvo no diretório original.")
        self.options_box.pack_start(self.chk_reset_ewc, False, False, 0)

        # Avaliação vs âncoras congeladas: métrica comparável entre sessões
        # (self-play puro tem alvo móvel — saldo oscila em torno de 0 por
        # construção e não diz se a política realmente melhorou).
        lbl_eval = Gtk.Label()
        lbl_eval.set_markup("<b>Eval Anchors</b>")
        lbl_eval.set_margin_top(10)
        lbl_eval.set_halign(Gtk.Align.START)
        self.options_box.pack_start(lbl_eval, False, False, 0)

        self.entry_eval_anchors = Gtk.Entry()
        self.entry_eval_anchors.set_placeholder_text(
            "vazio = sem avaliação; ex: ppo_models/A/ppo_full_checkpoint.pth, ppo_models/B/...")
        self.entry_eval_anchors.set_tooltip_text(
            "Caminhos de checkpoints .pth (separados por vírgula) usados como\n"
            "oponentes CONGELADOS de referência. A cada N iterações, a política\n"
            "atual joga contra cada âncora com ação determinística (sem sampling)\n"
            "e o resultado (win-rate, saldo) é gravado em eval_history.csv — a\n"
            "métrica que dá para comparar entre sessões de treino diferentes.")
        self.options_box.pack_start(self.entry_eval_anchors, False, False, 0)

        hbox_eval_interval = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        lbl_eval_interval = Gtk.Label(label="a cada (it.):")
        hbox_eval_interval.pack_start(lbl_eval_interval, False, False, 0)

        self.entry_eval_interval = Gtk.Entry()
        self.entry_eval_interval.set_text("20")
        self.entry_eval_interval.set_width_chars(5)
        hbox_eval_interval.pack_start(self.entry_eval_interval, True, True, 0)
        self.options_box.pack_start(hbox_eval_interval, False, False, 0)

        hbox_eval_episodes = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        lbl_eval_episodes = Gtk.Label(label="episódios/âncora:")
        hbox_eval_episodes.pack_start(lbl_eval_episodes, False, False, 0)

        self.entry_eval_episodes = Gtk.Entry()
        self.entry_eval_episodes.set_text("10")
        self.entry_eval_episodes.set_width_chars(4)
        hbox_eval_episodes.pack_start(self.entry_eval_episodes, True, True, 0)
        self.options_box.pack_start(hbox_eval_episodes, False, False, 0)

        lbl_run = Gtk.Label()
        lbl_run.set_markup("<b>Execução</b>")
        lbl_run.set_margin_top(10)
        lbl_run.set_halign(Gtk.Align.START)
        self.options_box.pack_start(lbl_run, False, False, 0)

        hbox_steps = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        lbl_steps = Gtk.Label(label="Timesteps:")
        hbox_steps.pack_start(lbl_steps, False, False, 0)

        self.entry_steps = Gtk.Entry()
        self.entry_steps.set_text("100000")
        hbox_steps.pack_start(self.entry_steps, True, True, 0)
        self.options_box.pack_start(hbox_steps, False, False, 0)

        hbox_envs = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        lbl_envs = Gtk.Label(label="Parallel Envs:")
        hbox_envs.pack_start(lbl_envs, False, False, 0)

        self.spin_envs = Gtk.SpinButton.new_with_range(1, 32, 1)
        self.spin_envs.set_value(1)
        hbox_envs.pack_start(self.spin_envs, True, True, 0)
        self.options_box.pack_start(hbox_envs, False, False, 0)

        # Model Selection (Retrain)
        lbl_model = Gtk.Label(label="Retrain Model:")
        lbl_model.set_halign(Gtk.Align.START)
        self.options_box.pack_start(lbl_model, False, False, 0)

        self.combo_model = Gtk.ComboBoxText()
        self.combo_model.append_text("None (Train from scratch)")
        self.combo_model.set_active(0)

        base_ppo = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../Attacker-AI-Training/PPO'))
        int_models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../src/strategy/entity'))

        mdirs = [
            os.path.join(base_ppo, 'ppo_models'),
            int_models_dir
        ]

        for mdir in mdirs:
            if os.path.exists(mdir):
                for d in os.listdir(mdir):
                    if os.path.isdir(os.path.join(mdir, d)):
                        self.combo_model.append_text(d)

        self.options_box.pack_start(self.combo_model, False, False, 0)

        # New Model Name
        lbl_new_name = Gtk.Label(label="Save Model As:")
        lbl_new_name.set_halign(Gtk.Align.START)
        lbl_new_name.set_margin_top(5)
        self.options_box.pack_start(lbl_new_name, False, False, 0)

        self.entry_new_name = Gtk.Entry()
        self.entry_new_name.set_text("unbrain_sim2real_model")
        self.options_box.pack_start(self.entry_new_name, False, False, 0)

        # Actions
        self.btn_start = Gtk.Button(label="Start Training (GPU)")
        self.btn_start.connect("clicked", self.on_start_clicked)
        self.btn_start.set_margin_top(10)
        self.options_box.pack_start(self.btn_start, False, False, 0)

        self.btn_stop = Gtk.Button(label="Stop / Save Model")
        self.btn_stop.connect("clicked", self.on_stop_clicked)
        self.btn_stop.set_sensitive(False)
        self.options_box.pack_start(self.btn_stop, False, False, 0)

        # Status / Progress
        self.lbl_status = Gtk.Label(label="Status: Idle")
        self.lbl_status.set_line_wrap(True)
        self.options_box.pack_start(self.lbl_status, False, False, 5)

        self.options_box.show_all()

        # ---> Criando o divisor ajustável (Gtk.Paned) <---
        paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        # O divisor vai expandir para preencher a tela
        self.pack_start(paned, True, True, 0) 

        # ---> Container da Parte Superior (Gráfico + Controles) <---
        graph_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        # Matplotlib Graph
        self.fig = Figure(figsize=(5, 3), dpi=90, constrained_layout=True)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Training Returns")
        self.ax.set_xlabel("Timesteps")
        self.ax.set_ylabel("Avg Return")
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.line, = self.ax.plot([], [], 'b-', alpha=0.3, label='Raw')
        self.line_ma, = self.ax.plot([], [], 'r-', linewidth=2, label='Moving Avg')
        self.ax.legend(loc='upper left', fontsize=8)

        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(-1, 300)
        graph_vbox.pack_start(self.canvas, True, True, 0)

        # Moving average window control
        hbox_ma = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lbl_ma = Gtk.Label(label="Janela Média Móvel:")
        hbox_ma.pack_start(lbl_ma, False, False, 0)
        self.ma_adj = Gtk.Adjustment(value=50, lower=1, upper=500, step_increment=10, page_increment=50)
        self.ma_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=self.ma_adj)
        self.ma_scale.set_digits(0)
        self.ma_scale.set_hexpand(True)
        self.ma_scale.connect("value-changed", self._on_ma_changed)
        hbox_ma.pack_start(self.ma_scale, True, True, 0)

        # Load CSV button
        self.btn_load_csv = Gtk.Button(label="📂 Carregar dataset.csv")
        self.btn_load_csv.connect("clicked", self._on_load_csv_clicked)
        hbox_ma.pack_start(self.btn_load_csv, False, False, 0)

        # Export current buffer to CSV
        self.btn_export_csv = Gtk.Button(label="💾 Exportar dados atuais")
        self.btn_export_csv.connect("clicked", self._on_export_csv_clicked)
        hbox_ma.pack_start(self.btn_export_csv, False, False, 0)

        graph_vbox.pack_start(hbox_ma, False, False, 0)
        
        # Adiciona a caixa do gráfico na metade de cima do divisor
        paned.pack1(graph_vbox, resize=True, shrink=False)

        # ---> Container da Parte Inferior (Log view) <---
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_propagate_natural_width(False)
        scrolled.set_propagate_natural_height(False)
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        scrolled.set_size_request(-1, 150)
        
        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textbuffer = self.textview.get_buffer()
        scrolled.add(self.textview)
        
        # Adiciona os logs na metade de baixo do divisor
        paned.pack2(scrolled, resize=True, shrink=False)
        
        # Data for plot
        self.plot_x = []
        self.plot_y = []
        self.versions = []
        self._autosave_counter = 0
        self._autosave_interval = 10  # salva a cada 10 batches
        
        self.show_all()

    def log(self, text):
        end_iter = self.textbuffer.get_end_iter()
        self.textbuffer.insert(end_iter, text + "\n")
        
        # Scroll to bottom
        adj = self.textview.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())

    def _moving_average(self, data, window):
        """Calcula média e desvio padrão móvel com pandas"""
        if len(data) == 0:
            return np.array([]), np.array([])
        import pandas as pd
        s = pd.Series(data)
        mv_mean = s.rolling(window=window, min_periods=1).mean().to_numpy()
        mv_std = s.rolling(window=window, min_periods=1).std(ddof=0).to_numpy()
        return mv_mean, mv_std

    def _on_ma_changed(self, widget):
        """Atualiza o gráfico quando a janela da média móvel muda"""
        self._redraw_plot()

    def _redraw_plot(self):
        """Redesenha o gráfico com média móvel e linhas de versão"""
        if not self.plot_x:
            return
            
        window = max(1, int(self.ma_adj.get_value()))
        self.line.set_data(self.plot_x, self.plot_y)
        
        # Remover shaded area do desvio padrão anterior, se existir
        if hasattr(self, 'fill_poly'):
            try:
                self.fill_poly.remove()
            except Exception:
                pass
            del self.fill_poly

        ma_data, std_data = self._moving_average(self.plot_y, window)
        
        if len(ma_data) > 0 and len(ma_data) == len(self.plot_x):
            self.line_ma.set_data(self.plot_x, ma_data)
            self.fill_poly = self.ax.fill_between(self.plot_x, ma_data - std_data, ma_data + std_data, color='red', alpha=0.30)
                
        # Limpar marcações de versão anteriores (para não sobrepor ao atualizar)
        [l.remove() for l in reversed(self.ax.lines) if l not in [self.line, self.line_ma]]
        [t.remove() for t in reversed(self.ax.texts)]
        
        # Desenha linha tracejada sempre que a versão mudar
        if hasattr(self, 'versions') and self.versions:
            last_v = self.versions[0]
            for i, v in enumerate(self.versions):
                if v != last_v:
                    x_val = self.plot_x[i]
                    self.ax.axvline(x=x_val, color='grey', linestyle='--', alpha=0.7)
                    y_max = max(self.plot_y) if self.plot_y else 0
                    self.ax.text(x_val, y_max, f" {v}", rotation=90, verticalalignment='top', alpha=0.7, fontsize=8)
                    last_v = v

        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def _on_load_csv_clicked(self, widget):
        """Abre diálogo para selecionar dataset.csv e carrega no gráfico"""
        dialog = Gtk.FileChooserDialog(
            title="Selecionar dataset.csv",
            parent=self.get_toplevel(),
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )
        f = Gtk.FileFilter()
        f.set_name("CSV files")
        f.add_pattern("*.csv")
        dialog.add_filter(f)

        # Tenta abrir já na pasta do modelo
        base_ppo = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../Attacker-AI-Training/PPO/ppo_models'))
        if os.path.exists(base_ppo):
            dialog.set_current_folder(base_ppo)
        
        dialog.set_show_hidden(True)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            path = dialog.get_filename()
            self._load_dataset_from_csv(path)
        dialog.destroy()

    def _load_dataset_from_csv(self, path):
        """Carrega dataset.csv e atualiza o gráfico com controle de versão"""
        try:
            import csv
            timesteps = []
            rewards = []
            versions = []
            with open(path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        t = float(row.get('t_so_far', 0))
                        r = float(row.get('avg_return', 0))
                        v = row.get('model_version', 'legacy')
                        timesteps.append(t)
                        rewards.append(r)
                        versions.append(v)
                    except (ValueError, TypeError):
                        continue
            if timesteps:
                self.plot_x = timesteps
                self.plot_y = rewards
                self.versions = versions
                self._redraw_plot()
                self.log(f"Dataset carregado: {len(timesteps)} pontos de {path}")
            else:
                self.log(f"Nenhum dado válido encontrado em {path}")
        except Exception as e:
            self.log(f"Erro ao carregar CSV: {e}")

    def update_plot(self, step, reward, version="unknown"):
        self.plot_x.append(step)
        self.plot_y.append(reward)
        self.versions.append(version)
        self._redraw_plot()
        
        self._autosave_counter += 1
        if self._autosave_counter % self._autosave_interval == 0:
            self._autosave_to_disk()

    def _autosave_to_disk(self):
        """Salva o buffer atual em CSV automaticamente, sem interação do usuário."""
        try:
            import csv
            model_name = self.entry_new_name.get_text() or "unbrain_live_model"
            base_ppo = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../Attacker-AI-Training/PPO/ppo_models'))
            model_dir = os.path.join(base_ppo, model_name)
            os.makedirs(model_dir, exist_ok=True)
            try: os.chmod(model_dir, 0o777)
            except: pass
            
            path = os.path.join(model_dir, 'ui_autosave.csv')
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['t_so_far', 'avg_return'])
                for t, r in zip(self.plot_x, self.plot_y):
                    writer.writerow([t, r])
                    
            try: os.chmod(path, 0o666) # <-- LIBERA O AUTOSAVE DA UI
            except: pass
            
            self.log(f"[Auto-save] {len(self.plot_x)} pontos salvos em {path}")
        except Exception as e:
            self.log(f"[Auto-save] Erro: {e}")

    def _on_export_csv_clicked(self, widget):
        """Exporta os dados do gráfico atual (buffer da UI) para um CSV sem parar o treino."""
        if not self.plot_x:
            self.log("Nenhum dado para exportar ainda.")
            return

        dialog = Gtk.FileChooserDialog(
            title="Salvar dados atuais como CSV",
            parent=self.get_toplevel(),
            action=Gtk.FileChooserAction.SAVE,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK,
        )
        dialog.set_current_name("training_history_export.csv")

        # Sugere pasta do modelo selecionado
        model_name = self.entry_new_name.get_text() or "unbrain_live_model"
        base_ppo = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../Attacker-AI-Training/PPO/ppo_models'))
        suggested = os.path.join(base_ppo, model_name)
        if os.path.exists(suggested):
            dialog.set_current_folder(suggested)
        elif os.path.exists(base_ppo):
            dialog.set_current_folder(base_ppo)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            path = dialog.get_filename()
            try:
                import csv
                with open(path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['t_so_far', 'avg_return'])
                    for t, r in zip(self.plot_x, self.plot_y):
                        writer.writerow([t, r])
                        
                try: os.chmod(path, 0o666) # <-- LIBERA O EXPORT DA UI
                except: pass
                
                self.log(f"✓ {len(self.plot_x)} pontos exportados para {path}")
            except Exception as e:
                self.log(f"Erro ao exportar: {e}")
        dialog.destroy()

    def on_chk_render_hlc_toggled(self, widget):
        enabled = widget.get_active()
        self.worker.set_render(enabled)

    def on_start_clicked(self, widget):
        try:
            steps = int(self.entry_steps.get_text())
        except ValueError:
            self.log("Error: Timesteps must be an integer.")
            return
            
        retrain_selection = self.combo_model.get_active_text()
        retrain_model = retrain_selection if retrain_selection and not retrain_selection.startswith("None") else None
            
        # Curriculum: só ativo pelos botões dedicados; eles também mandam no delay.
        # Sem curriculum, o delay segue o checkbox (stage fixo 4 -> delay pleno).
        use_curriculum = not self.radio_curr_off.get_active()
        if self.radio_curr_delay.get_active():
            apply_delay = True
        elif self.radio_curr_no_delay.get_active():
            apply_delay = False
        else:
            apply_delay = self.chk_apply_delay.get_active()
        delay_txt = self.entry_delay_frames.get_text().strip()

        config = {
            'use_vision_noise': self.chk_vision_noise.get_active(),
            'apply_delay': apply_delay,
            'use_curriculum': use_curriculum,
            'delay_frames': int(delay_txt) if delay_txt.isdigit() else None,
            'max_random_delay': 5,
            'anneal_shaping': self.chk_anneal_shaping.get_active(),
            'goal_reward_scale': 2.5 if self.chk_anneal_shaping.get_active() else 1.0,
            'ewc_lambda': float(self.entry_ewc_lambda.get_text()) if self.entry_ewc_lambda.get_text().strip().replace('.', '', 1).isdigit() else None,
            'reset_ewc': self.chk_reset_ewc.get_active(),
            'augment_delay_actions': self.chk_augment_obs.get_active(),
            'pbrs_move': self.chk_pbrs_move.get_active(),
            'eval_anchors': [p.strip() for p in self.entry_eval_anchors.get_text().split(',') if p.strip()],
            'eval_interval_iterations': int(self.entry_eval_interval.get_text()) if self.entry_eval_interval.get_text().isdigit() else 20,
            'eval_n_episodes': int(self.entry_eval_episodes.get_text()) if self.entry_eval_episodes.get_text().isdigit() else 10,
            'train_with_allies': self.chk_allies.get_active(),
            'render_hlc': self.chk_render_hlc.get_active(),
            'self_play_enabled': self.chk_self_play.get_active(),
            'self_play_1v2_enabled': self.chk_self_play_1v2.get_active(),
            'self_play_interval': int(self.entry_self_play_interval.get_text()) if self.entry_self_play_interval.get_text().isdigit() else 5,
            'timesteps': steps,
            'model_name': self.entry_new_name.get_text(),
            'retrain_model': retrain_model,
            'num_envs': int(self.spin_envs.get_value()),
            'vision_noise_config': self.world.get_noise_config() if hasattr(self.world, 'get_noise_config') else {}
        }
        
        self.plot_x = []
        self.plot_y = []
        self.versions = []
        self.line.set_data([], [])
        self.canvas.draw()
        
        if self.worker.start(config):
            self.btn_start.set_sensitive(False)
            self.btn_stop.set_sensitive(True)
            self.lbl_status.set_text("Status: Training...")
            self.log("Started PPO training process...")
            
            # Start polling for updates (16ms = ~60 FPS)
            self.timeout_id = GLib.timeout_add(16, self.poll_updates)

    def on_stop_clicked(self, widget):
        self.log("Sending stop signal to training worker...")
        self.worker.stop()
        self.btn_stop.set_sensitive(False)

    def poll_updates(self):
        updates = self.worker.get_updates()
        try:
            total_steps = int(self.entry_steps.get_text())
        except ValueError:
            total_steps = 0

        for up in updates:
            if not isinstance(up, dict):
                continue
            status = up.get('status')

            if status == 'initializing':
                self.log("Worker initializing environment and model...")
                if 'msg' in up:
                    self.log(up['msg'])
            elif status == 'dataset_migrated':
                dataset_path = up.get('path')
                if dataset_path and os.path.exists(dataset_path):
                    self.log(f"Pré-carregando histórico do modelo pai...")
                    self._load_dataset_from_csv(dataset_path)
            elif status == 'training':
                step = up.get('step', 0)
                reward = up.get('reward', 0)
                version = up.get('version', 'unknown') # <--- Captura
                self.lbl_status.set_text(f"Status: Training (Step {step} / {total_steps}) | Avg Reward: {reward:.2f}")
                self.update_plot(step, reward, version) # <--- Envia a versão
            elif status == 'render_state':
                if self.chk_render_hlc.get_active() and hasattr(self.world, 'update_from_rsoccer'):
                    self.world.update_from_rsoccer(up)
            elif status == 'stopping':
                self.log("Salvando checkpoint...")
                self.lbl_status.set_text("Status: Saving checkpoint...")
            elif status == 'stopped':
                self.log(f"Treino pausado! Checkpoint salvo em {up.get('model_path')}")
                if 'msg' in up:
                    self.log(up['msg'])
                # Carrega o dataset.csv automaticamente para atualizar o gráfico
                dataset_path = up.get('dataset_path')
                if dataset_path and os.path.exists(dataset_path):
                    self.log(f"Carregando histórico completo do dataset...")
                    self._load_dataset_from_csv(dataset_path)
                self.reset_ui()
                return False

            elif status == 'finished':
                self.log(f"Training finished successfully! Model saved at {up.get('model_path')}")
                self.reset_ui()
                return False  # Stop polling
            elif status == 'error':
                self.log(f"Training Error: {up.get('error_msg')}")
                self.reset_ui()
                return False  # Stop polling

        return True  # Continue polling

    def reset_ui(self):
        self.btn_start.set_sensitive(True)
        self.btn_stop.set_sensitive(False)
        self.lbl_status.set_text("Status: Idle")
        if self.timeout_id:
            GLib.source_remove(self.timeout_id)
            self.timeout_id = None
