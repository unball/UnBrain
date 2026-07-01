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
        
        # Title
        lbl_title = Gtk.Label()
        lbl_title.set_markup("<span size='x-large' weight='bold'>AI Training (EWC + Sim-to-Real)</span>")
        self.pack_start(lbl_title, False, False, 10)
        
        # Config options
        hbox_cfg = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        self.chk_vision_noise = Gtk.CheckButton(label="Apply Vision Noise (Domain Randomization)")
        self.chk_vision_noise.set_active(True)
        hbox_cfg.pack_start(self.chk_vision_noise, False, False, 0)

        self.chk_apply_delay = Gtk.CheckButton(label="Apply Network Delay (~50ms)")
        self.chk_apply_delay.set_active(True)
        hbox_cfg.pack_start(self.chk_apply_delay, False, False, 0)
        
        self.chk_allies = Gtk.CheckButton(label="Train AI + Classic Entities (3 Robots)")
        self.chk_allies.set_active(False)
        hbox_cfg.pack_start(self.chk_allies, False, False, 0)

        self.chk_render_hlc = Gtk.CheckButton(label="Draw HLC (Render rSoccer Field)")
        self.chk_render_hlc.set_active(False)
        self.chk_render_hlc.connect("toggled", self.on_chk_render_hlc_toggled)
        hbox_cfg.pack_start(self.chk_render_hlc, False, False, 0)
        
        self.pack_start(hbox_cfg, False, False, 5)
        
        # Self-Play config
        hbox_sp = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.pack_start(hbox_sp, False, False, 5)
        
        self.chk_self_play = Gtk.CheckButton(label="Enable 1v1 Self-Play")
        self.chk_self_play.set_active(True)
        hbox_sp.pack_start(self.chk_self_play, False, False, 0)
        
        self.chk_self_play_1v2 = Gtk.CheckButton(label="Self Play 1v2")
        self.chk_self_play_1v2.set_active(False)
        hbox_sp.pack_start(self.chk_self_play_1v2, False, False, 0)
        
        lbl_sp_interval = Gtk.Label(label="Save Interval (Iterations):")
        hbox_sp.pack_start(lbl_sp_interval, False, False, 0)
        
        self.entry_self_play_interval = Gtk.Entry()
        self.entry_self_play_interval.set_text("5")
        self.entry_self_play_interval.set_width_chars(5)
        hbox_sp.pack_start(self.entry_self_play_interval, False, False, 0)
        
        hbox_cfg2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.pack_start(hbox_cfg2, False, False, 5)
        
        lbl_steps = Gtk.Label(label="Timesteps:")
        hbox_cfg2.pack_start(lbl_steps, False, False, 0)
        
        self.entry_steps = Gtk.Entry()
        self.entry_steps.set_text("100000")
        hbox_cfg2.pack_start(self.entry_steps, False, False, 0)
        
        lbl_envs = Gtk.Label(label="Parallel Envs:")
        hbox_cfg2.pack_start(lbl_envs, False, False, 0)
        
        self.spin_envs = Gtk.SpinButton.new_with_range(1, 32, 1)
        self.spin_envs.set_value(1)
        hbox_cfg2.pack_start(self.spin_envs, False, False, 0)

        
        # Model Selection (Retrain)
        lbl_model = Gtk.Label(label="Retrain Model:")
        hbox_cfg2.pack_start(lbl_model, False, False, 0)
        
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
        
        hbox_cfg2.pack_start(self.combo_model, False, False, 0)
        
        # New Model Name
        hbox_cfg3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lbl_new_name = Gtk.Label(label="Save Model As:")
        hbox_cfg3.pack_start(lbl_new_name, False, False, 0)
        
        self.entry_new_name = Gtk.Entry()
        self.entry_new_name.set_text("unbrain_sim2real_model")
        hbox_cfg3.pack_start(self.entry_new_name, False, False, 0)
        
        self.pack_start(hbox_cfg3, False, False, 0)
        
        # Actions
        hbox_actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        self.btn_start = Gtk.Button(label="Start Training (GPU)")
        self.btn_start.connect("clicked", self.on_start_clicked)
        hbox_actions.pack_start(self.btn_start, True, True, 0)
        
        self.btn_stop = Gtk.Button(label="Stop / Save Model")
        self.btn_stop.connect("clicked", self.on_stop_clicked)
        self.btn_stop.set_sensitive(False)
        hbox_actions.pack_start(self.btn_stop, True, True, 0)
        
        self.pack_start(hbox_actions, False, False, 10)
        
        # Status / Progress
        self.lbl_status = Gtk.Label(label="Status: Idle")
        self.pack_start(self.lbl_status, False, False, 0)
        
        # Matplotlib Graph
        self.fig = Figure(figsize=(5, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Training Returns")
        self.ax.set_xlabel("Timesteps")
        self.ax.set_ylabel("Avg Return")
        self.line, = self.ax.plot([], [], 'b-', alpha=0.3, label='Raw')
        self.line_ma, = self.ax.plot([], [], 'r-', linewidth=2, label='Moving Avg')
        self.ax.legend(loc='upper left', fontsize=8)

        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(-1, 200)
        self.pack_start(self.canvas, True, True, 0)

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

        # Export current buffer to CSV (without stopping training)
        self.btn_export_csv = Gtk.Button(label="💾 Exportar dados atuais")
        self.btn_export_csv.connect("clicked", self._on_export_csv_clicked)
        hbox_ma.pack_start(self.btn_export_csv, False, False, 0)

        self.pack_start(hbox_ma, False, False, 0)

        
        # Data for plot
        self.plot_x = []
        self.plot_y = []
        self.versions = []
        self._autosave_counter = 0
        self._autosave_interval = 10  # salva a cada 10 batches

        # Log view
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        scrolled.set_size_request(-1, 150)
        
        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textbuffer = self.textview.get_buffer()
        scrolled.add(self.textview)
        
        self.pack_start(scrolled, True, True, 0)
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
            
        config = {
            'use_vision_noise': self.chk_vision_noise.get_active(),
            'apply_delay': self.chk_apply_delay.get_active(),
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
