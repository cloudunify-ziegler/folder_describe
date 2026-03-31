import os
import subprocess
import tkinter as tk
from tkinter import filedialog


def main():
    # 1. Root Window für Tkinter verstecken
    root = tk.Tk()
    root.withdraw()

    # 2. Verzeichnis auswählen, das analysiert werden soll
    selected_dir = filedialog.askdirectory(title="Verzeichnis für Analyse auswählen")
    if not selected_dir:
        print("Kein Verzeichnis ausgewählt. Beende Vorgang.")
        return

    # 3. Pfade festlegen
    # Der Ordnername des Ziels (für den Dateinamen)
    folder_name = os.path.basename(os.path.normpath(selected_dir))

    # Das Verzeichnis, in dem das Skript gerade ausgeführt wird
    current_working_dir = os.getcwd()

    # Dateiname zusammenbauen
    filename = f"{folder_name}_analysis.txt"
    # Die Datei wird im aktuellen Verzeichnis des Tools erstellt, nicht im Zielordner
    output_file = os.path.join(current_working_dir, filename)

    print(f"Starte Analyse von: {selected_dir}")
    print(f"Ergebnis wird gespeichert in: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        # Header
        f.write(f"PROJEKT-ANALYSE: {folder_name}\n")
        f.write(f"Pfad: {selected_dir}\n")
        f.write("=" * 40 + "\n\n")

        # Step 1: Directory Tree
        f.write("VERZEICHNIS-STRUKTUR:\n")
        try:
            # Versuche den System-Befehl 'tree' (funktioniert auf Linux/Mac und oft Windows)
            tree_output = subprocess.run(['tree', selected_dir], capture_output=True, text=True, encoding='utf-8')
            if tree_output.returncode == 0:
                f.write(tree_output.stdout)
            else:
                raise FileNotFoundError
        except (FileNotFoundError, Exception):
            # Fallback: Manuelle Auflistung via os.walk
            f.write("(Tree-Befehl nicht verfügbar - Fallback auf manuelle Liste)\n")
            for root_dir, dirs, files in os.walk(selected_dir):
                level = root_dir.replace(selected_dir, '').count(os.sep)
                indent = ' ' * 4 * level
                f.write(f"{indent}{os.path.basename(root_dir)}/\n")
                sub_indent = ' ' * 4 * (level + 1)
                for file in files:
                    f.write(f"{sub_indent}{file}\n")

        f.write("\n\n" + "=" * 40 + "\n")

        # Step 2: Datei-Inhalte auslesen
        # Ich habe .json und .md hinzugefügt, da diese für "andere Codes" oft wichtig sind
        extensions = ('.py', '.xml', '.css', '.scss', '.js', '.csv', '.json', '.md')
        f.write("DATEI-INHALTE:\n\n")

        for root_dir, _, files in os.walk(selected_dir):
            for file in files:
                if file.lower().endswith(extensions):
                    full_path = os.path.join(root_dir, file)

                    # Relativer Pfad für bessere Übersichtlichkeit im Textfile
                    rel_path = os.path.relpath(full_path, selected_dir)

                    f.write(f"FILE: {rel_path}\n")
                    f.write("-" * 20 + "\n")
                    try:
                        with open(full_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            f.write(content + "\n")
                    except Exception as e:
                        f.write(f"[FEHLER beim Lesen: {str(e)}]\n")
                    f.write("\n" + "#" * 40 + "\n\n")

    print(f"\nFertig! Datei erfolgreich erstellt: {filename}")


if __name__ == "__main__":
    main()