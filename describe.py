import os
import subprocess
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from pathlib import Path
import ast

def get_odoo_module_name(directory):
    """
    Versucht den Modulnamen aus der __manifest__.py zu extrahieren.
    Fällt auf den Ordnernamen zurück, falls nicht vorhanden.
    - zmi / cloudunify
    """
    manifest_path = Path(directory) / "__manifest__.py"
    if manifest_path.exists():
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                data = ast.literal_eval(f.read())
                return data.get('name', Path(directory).name)
        except Exception:
            return Path(directory).name
    return Path(directory).name

def main():
    # 1. Root Window für Tkinter verstecken und in den Vordergrund zwingen
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)  # zmi / cloudunify: Fenster in den Fokus zwingen

    # 2. Verzeichnis auswählen
    selected_dir = filedialog.askdirectory(title="Verzeichnis für Analyse auswählen")
    if not selected_dir:
        print("Kein Verzeichnis ausgewählt. Beende Vorgang.")
        return

    # 3. Pfade und Dateinamen festlegen
    target_path = Path(selected_dir)
    folder_name = target_path.name
    project_display_name = get_odoo_module_name(selected_dir)

    current_working_dir = Path.cwd()
    # Dateiname ist nun exakt der Projektname (oder Ordnername)
    filename = f"{folder_name}.txt"
    output_file = current_working_dir / filename

    print(f"Starte Analyse von: {selected_dir}")
    print(f"Ergebnis wird gespeichert in: {output_file}")

    # 4. Relevante Endungen für Odoo-Entwicklung inkl. HTML für App-Store Descriptions
    extensions = (
        '.py', '.xml', '.css', '.scss', '.js',
        '.csv', '.json', '.md', '.rst', '.po', '.html'
    )

    with open(output_file, 'w', encoding='utf-8') as f:
        # Header (Wieder in Deutsch gemäß Original-Logik)
        f.write(f"PROJEKT-ANALYSE: {project_display_name}\n")
        f.write(f"Pfad: {selected_dir}\n")
        f.write(f"Exportzeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")

        # Step 1: Directory Tree
        f.write("VERZEICHNIS-STRUKTUR:\n")
        try:
            # System-Tree (ohne /f, damit wir nur Ordner sehen, exakt wie im Original)
            tree_output = subprocess.run(
                ['tree', str(target_path)],
                capture_output=True, text=True, encoding='utf-8'
            )
            if tree_output.returncode == 0:
                f.write(tree_output.stdout)
            else:
                raise FileNotFoundError
        except (FileNotFoundError, Exception):
            # Fallback: Manuelle Liste
            f.write("(Tree-Befehl nicht verfügbar - Fallback auf manuelle Liste)\n")
            for root_dir, dirs, files in os.walk(selected_dir):
                # zmi / cloudunify: Verhindert, dass der Fallback den .git Ordner durchsucht
                if '.git' in dirs:
                    dirs.remove('.git')

                # Berechnung der Einrückung
                level = Path(root_dir).relative_to(target_path).parts
                indent = ' ' * 4 * len(level)
                f.write(f"{indent}{Path(root_dir).name}/\n")

                sub_indent = ' ' * 4 * (len(level) + 1)
                for file in files:
                    f.write(f"{sub_indent}{file}\n")

        f.write("\n\n" + "=" * 60 + "\n")

        # Step 2: Datei-Inhalte auslesen
        f.write("DATEI-INHALTE:\n\n")

        for root_dir, dirs, files in os.walk(selected_dir):
            # zmi / cloudunify: Performance-Boost: Ignoriere das Abtauchen in .git Verzeichnisse komplett
            if '.git' in dirs:
                dirs.remove('.git')
            # Optimiere auch __pycache__, da kompilierte Python-Files für den Export irrelevant sind
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')

            for file in files:
                if file.lower().endswith(extensions):
                    full_path = Path(root_dir) / file
                    rel_path = full_path.relative_to(target_path)

                    f.write(f"FILE: {rel_path}\n")
                    f.write("-" * 30 + "\n")

                    try:
                        with open(full_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            f.write(content + "\n")
                    except Exception as e:
                        f.write(f"[FEHLER beim Lesen: {str(e)}]\n")

                    f.write("\n" + "#" * 60 + "\n\n")

    print(f"\nFertig! Datei erfolgreich erstellt: {filename}")

if __name__ == "__main__":
    main()