import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import time
import urllib.request
import urllib.parse
from html.parser import HTMLParser

class LinkExtractor(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.links = set()

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'a':
            for attr, value in attrs:
                if attr.lower() == 'href' and value:
                    if value.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
                        continue
                    absolute_url = urllib.parse.urljoin(self.base_url, value)
                    self.links.add(absolute_url)

class LinkCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vérificateur de liens sécurisé (Interne & Externe)")
        self.root.geometry("900x600")

        self.is_running = False

        # --- Haut : Entrée URL et boutons ---
        top_frame = tk.Frame(root, padx=10, pady=10)
        top_frame.pack(fill=tk.X)

        tk.Label(top_frame, text="URL du site :", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
        
        self.url_entry = tk.Entry(top_frame, font=("Arial", 11), width=45)
        self.url_entry.insert(0, "http://localhost/")
        self.url_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.btn_start = tk.Button(top_frame, text="Lancer l'analyse", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), command=self.start_analysis)
        self.btn_start.pack(side=tk.LEFT, padx=5)

        self.btn_stop = tk.Button(top_frame, text="Arrêter", bg="#c0392b", fg="white", font=("Arial", 10, "bold"), state=tk.DISABLED, command=self.stop_analysis)
        self.btn_stop.pack(side=tk.LEFT, padx=5)

        # --- Bas : Grille avec les deux cadres (Logs et Erreurs) ---
        grid_frame = tk.Frame(root, padx=10, pady=10)
        grid_frame.pack(fill=tk.BOTH, expand=True)
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
        grid_frame.rowconfigure(1, weight=1)

        # Cadre gauche : Roulement (Logs)
        tk.Label(grid_frame, text="Roulement du site (Logs en direct)", font=("Arial", 11, "bold"), fg="#34495e").grid(row=0, column=0, sticky="w", pady=5)
        self.log_box = scrolledtext.ScrolledText(grid_frame, bg="#1e1e1e", fg="#00ff66", font=("Courier", 10))
        self.log_box.grid(row=1, column=0, sticky="nsew", padx=(0, 5))

        # Cadre droite : Rapport d'erreurs
        tk.Label(grid_frame, text="Rapport des erreurs (Liens cassés)", font=("Arial", 11, "bold"), fg="#c0392b").grid(row=0, column=1, sticky="w", pady=5)
        self.report_box = scrolledtext.ScrolledText(grid_frame, bg="#1e1e1e", fg="#ff6b6b", font=("Courier", 10))
        self.report_box.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        self.report_box.insert(tk.END, "Aucune erreur détectée pour l'instant.\n")

    def log(self, message):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)

    def report_error(self, url, status, source_page=""):
        if "Aucune erreur" in self.report_box.get("1.0", tk.END):
            self.report_box.delete("1.0", tk.END)
        
        error_msg = f"[{status}] {url}\n"
        if source_page:
            error_msg += f"   ↳ Présent sur : {source_page}\n"
        error_msg += "\n"
        
        self.report_box.insert(tk.END, error_msg)
        self.report_box.see(tk.END)

    def start_analysis(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Erreur", "Veuillez entrer une URL valide.")
            return

        self.log_box.delete("1.0", tk.END)
        self.report_box.delete("1.0", tk.END)
        self.report_box.insert(tk.END, "Aucune erreur détectée pour l'instant.\n")

        self.is_running = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)

        threading.Thread(target=self.run_crawler, args=(url,), daemon=True).start()

    def stop_analysis(self):
        self.is_running = False
        self.log("\n[Arrêt demandé par l'utilisateur...]")
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)

    def check_url_status(self, url):
        status_code = 0
        # En-têtes complets pour imiter un navigateur réel
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.9',
            'Accept-Encoding': 'identity',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as response:
                status_code = response.getcode()
        except urllib.error.HTTPError as e:
            status_code = e.code
        except Exception:
            status_code = 0
        return status_code

    def run_crawler(self, base_url):
        parsed_base = urllib.parse.urlparse(base_url)
        base_domain = parsed_base.netloc

        visited = set()
        checked_external = set()
        queue = [base_url]
        delay = 0

        self.log(f"Début de l'analyse globale pour : {base_url}\n")

        while queue and self.is_running:
            current_url = queue.pop(0)

            if current_url in visited:
                continue

            visited.add(current_url)
            self.log(f"Vérification page interne : {current_url}")

            html_content = ""
            status_code = self.check_url_status(current_url)

            if status_code >= 400 or status_code == 0:
                self.report_error(current_url, status_code, "Lien direct / Page d'entrée")
                self.log(f"  -> ERREUR [Statut: {status_code}]")
            else:
                self.log(f"  -> OK [Statut: {status_code}]")
                
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
                    req = urllib.request.Request(current_url, headers=headers)
                    with urllib.request.urlopen(req, timeout=5) as response:
                        if 'text/html' in response.headers.get('Content-Type', ''):
                            html_content = response.read().decode('utf-8', errors='ignore')
                except Exception:
                    pass

                if html_content:
                    parser = LinkExtractor(current_url)
                    parser.feed(html_content)

                    for link in parser.links:
                        parsed_link = urllib.parse.urlparse(link)
                        clean_link = parsed_link._replace(fragment='').geturl()

                        if parsed_link.netloc == base_domain:
                            if clean_link not in visited and clean_link not in queue:
                                queue.append(clean_link)
                        else:
                            if clean_link not in checked_external:
                                checked_external.add(clean_link)
                                self.log(f"  [Externe] Test de : {clean_link}")
                                ext_status = self.check_url_status(clean_link)
                                if ext_status >= 400 or ext_status == 0:
                                    self.report_error(clean_link, ext_status, current_url)
                                    self.log(f"    -> ERREUR EXTERNE [Statut: {ext_status}]")
                                time.sleep(1)

            time.sleep(delay)

        if self.is_running:
            self.log(f"\n--- Analyse terminée. Pages internes explorées : {len(visited)} | Liens externes vérifiés : {len(checked_external)} ---")
        
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.is_running = False

if __name__ == "__main__":
    root = tk.Tk()
    app = LinkCheckerApp(root)
    root.mainloop()
