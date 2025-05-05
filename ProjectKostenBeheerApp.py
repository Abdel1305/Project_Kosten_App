import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class KostenBeheerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Projectmanagement Kostenbeheer")
        self.root.geometry("1200x900")

        self._setup_styles()

        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self._initialize_data()
        self._create_tabs()

    def _setup_styles(self):
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))
        style.configure('Treeview', font=('Arial', 10), rowheight=25)
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))

        # Kleurcodering voor Treeview
        style.map("Treeview", background=[("selected", "#5a9bd3")])  # Donkerder blauw voor geselecteerde regels
        style.configure("GreenRow.Treeview", background="#d4f7d4")  # Groen voor positieve winst
        style.configure("RedRow.Treeview", background="#f7d4d4")  # Rood voor negatieve winst

    def _initialize_data(self):
        self.budget_records = []  # Lijst met budgetten
        self.detail_records = []  # Lijst met detailregels

    def _create_tabs(self):
        self._create_table_tab()
        self._create_charts_tab()
        self._create_management_tab()

    def _create_table_tab(self):
        """Maak het tabblad voor de tabel."""
        table_tab = ttk.Frame(self.notebook)
        self.notebook.add(table_tab, text="📋 Tabeloverzicht")

        # Treeview voor tabelweergave
        columns = ("Kostenonderdeel", "Gedekt", "Gemaakt", "Toekomstig", "Winst/Verlies")
        self.tabel_tree = ttk.Treeview(table_tab, columns=columns, show="headings")

        for col in columns:
            self.tabel_tree.heading(col, text=col)
            self.tabel_tree.column(col, width=150)

        self.tabel_tree.pack(fill=tk.BOTH, expand=True)

        # Voeg een scrollbar toe
        scrollbar = ttk.Scrollbar(table_tab, orient="vertical", command=self.tabel_tree.yview)
        self.tabel_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Bind selectie van een rij aan een functie
        self.tabel_tree.bind("<<TreeviewSelect>>", self.show_detail_window)

        # Frame voor detailregels onderaan
        self.detail_window_frame = ttk.LabelFrame(table_tab, text="Detailregels voor geselecteerd kostenonderdeel")
        self.detail_window_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.detail_window_tree = ttk.Treeview(self.detail_window_frame, columns=("ID", "Onderdeel", "Type", "Bedrag", "Omschrijving", "Datum"), show="headings")
        self.detail_window_tree.heading("ID", text="ID")
        self.detail_window_tree.heading("Onderdeel", text="Onderdeel")
        self.detail_window_tree.heading("Type", text="Type")
        self.detail_window_tree.heading("Bedrag", text="Bedrag")
        self.detail_window_tree.heading("Omschrijving", text="Omschrijving")
        self.detail_window_tree.heading("Datum", text="Datum")

        # Stel kolombreedtes in
        self.detail_window_tree.column("ID", width=50)
        self.detail_window_tree.column("Onderdeel", width=150)
        self.detail_window_tree.column("Type", width=100)
        self.detail_window_tree.column("Bedrag", width=100)
        self.detail_window_tree.column("Omschrijving", width=200)
        self.detail_window_tree.column("Datum", width=120)

        self.detail_window_tree.pack(fill=tk.BOTH, expand=True)

    def refresh_tabeloverzicht(self):
        """Vernieuw de data in het Tabeloverzicht."""
        # Wis de huidige inhoud van de tabel
        for item in self.tabel_tree.get_children():
            self.tabel_tree.delete(item)

        # Bereken en voeg data toe aan de tabel
        kosten_data = self._calculate_kosten_data()
        for record in kosten_data:
            kostenonderdeel, gedekt, gemaakt, toekomstig, winst_verlies = record

            # Verwijder het valuta-teken (€) en converteer Winst/Verlies naar een numerieke waarde
            winst_verlies_num = float(winst_verlies.replace("€", "").replace(",", "").replace(".", "."))

            # Bepaal de tag voor conditionele opmaak
            if winst_verlies_num > 0:
                tag = "GreenRow"
            else:
                tag = "RedRow"

            # Voeg de rij toe met de overeenkomstige tag
            self.tabel_tree.insert("", "end", values=record, tags=(tag,))

        # Pas de tags toe
        self.tabel_tree.tag_configure("GreenRow", background="#d4f7d4")
        self.tabel_tree.tag_configure("RedRow", background="#f7d4d4")

    def _calculate_kosten_data(self):
        """Bereken de gegevens voor de tabel."""
        kosten_dict = {}

        # Verwerk budgetten
        for record in self.budget_records:
            onderdeel, bedrag = record[1], float(record[2])
            if onderdeel not in kosten_dict:
                kosten_dict[onderdeel] = {"Gedekt": bedrag, "Gemaakt": 0, "Toekomstig": 0}
            else:
                kosten_dict[onderdeel]["Gedekt"] += bedrag

        # Verwerk detailregels
        for record in self.detail_records:
            onderdeel, detail_type, bedrag = record[1], record[2], float(record[3])
            if onderdeel not in kosten_dict:
                kosten_dict[onderdeel] = {"Gedekt": 0, "Gemaakt": 0, "Toekomstig": 0}

            if detail_type == "Gemaakt":
                kosten_dict[onderdeel]["Gemaakt"] += bedrag
            elif detail_type == "Toekomstig":
                kosten_dict[onderdeel]["Toekomstig"] += bedrag

        # Bereken winst/verlies en maak de data klaar voor de tabel
        kosten_data = []
        for onderdeel, values in kosten_dict.items():
            gedekt = values["Gedekt"]
            gemaakt = values["Gemaakt"]
            toekomstig = values["Toekomstig"]
            winst_verlies = gedekt - (gemaakt + toekomstig)
            kosten_data.append((onderdeel, f"€{gedekt:,.2f}", f"€{gemaakt:,.2f}", f"€{toekomstig:,.2f}", f"€{winst_verlies:,.2f}"))

        return kosten_data

    def show_detail_window(self, event):
        """Toon detailregels in een nieuw venster onderaan voor geselecteerd kostenonderdeel."""
        # Wis de huidige inhoud van de detailregels tabel
        for item in self.detail_window_tree.get_children():
            self.detail_window_tree.delete(item)

        # Haal het geselecteerde kostenonderdeel op
        selected_item = self.tabel_tree.selection()
        if not selected_item:
            return

        selected_values = self.tabel_tree.item(selected_item, "values")
        if not selected_values:
            return

        selected_kostenonderdeel = selected_values[0]

        # Voeg de detailregels toe die bij dit kostenonderdeel horen
        for detail in self.detail_records:
            if detail[1] == selected_kostenonderdeel:
                self.detail_window_tree.insert("", "end", values=detail)

    def _create_charts_tab(self):
        """Maak het tabblad voor grafieken."""
        charts_tab = ttk.Frame(self.notebook)
        self.notebook.add(charts_tab, text="📊 Grafieken")

        label = ttk.Label(charts_tab, text="Hier komen de grafieken.", font=("Arial", 12))
        label.pack(pady=20)

    def _create_management_tab(self):
        """Maak het tabblad voor beheer."""
        management_tab = ttk.Frame(self.notebook)
        self.notebook.add(management_tab, text="⚙️ Beheer")

        # Frame voor toevoegen van budgetten
        budget_input_frame = ttk.LabelFrame(management_tab, text="Budget toevoegen")
        budget_input_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(budget_input_frame, text="Kostenonderdeel:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.budget_component = ttk.Entry(budget_input_frame)
        self.budget_component.grid(row=0, column=1, sticky="we", padx=5, pady=5)

        ttk.Label(budget_input_frame, text="Bedrag:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.budget_amount = ttk.Entry(budget_input_frame)
        self.budget_amount.grid(row=1, column=1, sticky="we", padx=5, pady=5)

        ttk.Label(budget_input_frame, text="Omschrijving:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.budget_description = ttk.Entry(budget_input_frame)
        self.budget_description.grid(row=2, column=1, sticky="we", padx=5, pady=5)

        ttk.Button(budget_input_frame, text="Budget toevoegen", command=self.add_budget).grid(row=3, column=1, sticky="e", padx=5, pady=5)

        # Frame voor toevoegen van detailregels
        detail_input_frame = ttk.LabelFrame(management_tab, text="Detailregel toevoegen")
        detail_input_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(detail_input_frame, text="Kostenonderdeel:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.detail_component = ttk.Combobox(detail_input_frame, values=[])
        self.detail_component.grid(row=0, column=1, sticky="we", padx=5, pady=5)

        ttk.Label(detail_input_frame, text="Type:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.detail_type = ttk.Combobox(detail_input_frame, values=["Gemaakt", "Toekomstig"])
        self.detail_type.grid(row=1, column=1, sticky="we", padx=5, pady=5)
        self.detail_type.current(0)

        ttk.Label(detail_input_frame, text="Bedrag:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.detail_amount = ttk.Entry(detail_input_frame)
        self.detail_amount.grid(row=2, column=1, sticky="we", padx=5, pady=5)

        ttk.Label(detail_input_frame, text="Omschrijving:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.detail_description = ttk.Entry(detail_input_frame)
        self.detail_description.grid(row=3, column=1, sticky="we", padx=5, pady=5)

        ttk.Button(detail_input_frame, text="Detailregel toevoegen", command=self.add_detail_row).grid(row=4, column=1, sticky="e", padx=5, pady=5)

        # Frame voor overzicht en verwijderfuncties
        overview_frame = ttk.Frame(management_tab)
        overview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Overzicht budgetten
        budget_tree_frame = ttk.LabelFrame(overview_frame, text="Overzicht budgetten")
        budget_tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.budget_tree = ttk.Treeview(budget_tree_frame, columns=("ID", "Onderdeel", "Bedrag", "Omschrijving", "Datum"), show="headings")
        self.budget_tree.heading("ID", text="ID")
        self.budget_tree.heading("Onderdeel", text="Onderdeel")
        self.budget_tree.heading("Bedrag", text="Bedrag")
        self.budget_tree.heading("Omschrijving", text="Omschrijving")
        self.budget_tree.heading("Datum", text="Datum")
        self.budget_tree.column("ID", width=50)
        self.budget_tree.column("Onderdeel", width=150)
        self.budget_tree.column("Bedrag", width=100)
        self.budget_tree.column("Omschrijving", width=200)
        self.budget_tree.column("Datum", width=120)
        self.budget_tree.pack(fill=tk.BOTH, expand=True)

        ttk.Button(budget_tree_frame, text="Verwijder geselecteerd budget", command=self.delete_budget).pack(pady=5)

        # Overzicht detailregels
        detail_tree_frame = ttk.LabelFrame(overview_frame, text="Overzicht detailregels")
        detail_tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.detail_tree = ttk.Treeview(detail_tree_frame, columns=("ID", "Onderdeel", "Type", "Bedrag", "Omschrijving", "Datum"), show="headings")
        self.detail_tree.heading("ID", text="ID")
        self.detail_tree.heading("Onderdeel", text="Onderdeel")
        self.detail_tree.heading("Type", text="Type")
        self.detail_tree.heading("Bedrag", text="Bedrag")
        self.detail_tree.heading("Omschrijving", text="Omschrijving")
        self.detail_tree.heading("Datum", text="Datum")

        # Stel kolombreedtes in
        self.detail_tree.column("ID", width=50)
        self.detail_tree.column("Onderdeel", width=150)
        self.detail_tree.column("Type", width=100)
        self.detail_tree.column("Bedrag", width=100)
        self.detail_tree.column("Omschrijving", width=200)
        self.detail_tree.column("Datum", width=120)

        self.detail_tree.pack(fill=tk.BOTH, expand=True)

        ttk.Button(detail_tree_frame, text="Verwijder geselecteerde detailregel", command=self.delete_detail).pack(pady=5)

    def add_budget(self):
        """Voegt een budget toe aan het overzicht."""
        component = self.budget_component.get()
        amount = self.budget_amount.get()
        description = self.budget_description.get()

        if not all([component, amount, description]):
            messagebox.showerror("Fout", "Vul alle velden in.")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Fout", "Voer een geldig bedrag in.")
            return

        record_id = len(self.budget_records) + 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        budget = (record_id, component, amount, description, timestamp)
        self.budget_records.append(budget)

        # Voeg toe aan de Treeview
        self.budget_tree.insert("", "end", values=budget)

        # Werk de combobox voor detailregels bij
        self.refresh_detail_combobox()

        self.refresh_tabeloverzicht()

    def delete_budget(self):
        """Verwijdert een geselecteerd budget, inclusief de gekoppelde detailregels."""
        selected_item = self.budget_tree.selection()
        if not selected_item:
            messagebox.showerror("Fout", "Selecteer eerst een budget om te verwijderen.")
            return

        for item in selected_item:
            values = self.budget_tree.item(item, "values")
            budget_id = int(values[0])
            budget_component = values[1]

            # Verwijder gekoppelde detailregels
            self.detail_records = [record for record in self.detail_records if record[1] != budget_component]
            for child in self.detail_tree.get_children():
                detail_values = self.detail_tree.item(child, "values")
                if detail_values[1] == budget_component:
                    self.detail_tree.delete(child)

            # Verwijder het budget zelf
            self.budget_tree.delete(item)
            self.budget_records = [record for record in self.budget_records if record[0] != budget_id]

        # Werk de combobox voor detailregels bij
        self.refresh_detail_combobox()

        self.refresh_tabeloverzicht()

    def refresh_detail_combobox(self):
        """Werk de combobox voor kostenonderdelen in de detailregels bij."""
        kostenonderdelen = [record[1] for record in self.budget_records]
        self.detail_component["values"] = kostenonderdelen

    def add_detail_row(self):
        """Voegt een detailregel toe aan het overzicht."""
        component = self.detail_component.get()
        detail_type = self.detail_type.get()
        amount = self.detail_amount.get()
        description = self.detail_description.get()

        if not all([component, detail_type, amount, description]):
            messagebox.showerror("Fout", "Vul alle velden in.")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Fout", "Voer een geldig bedrag in.")
            return

        record_id = len(self.detail_records) + 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        detail = (record_id, component, detail_type, amount, description, timestamp)
        self.detail_records.append(detail)

        # Voeg toe aan de Treeview
        self.detail_tree.insert("", "end", values=detail)

        self.refresh_tabeloverzicht()

    def delete_detail(self):
        """Verwijdert een geselecteerde detailregel."""
        selected_item = self.detail_tree.selection()
        if not selected_item:
            messagebox.showerror("Fout", "Selecteer eerst een detailregel om te verwijderen.")
            return

        for item in selected_item:
            values = self.detail_tree.item(item, "values")
            self.detail_tree.delete(item)

            # Verwijder uit detail_records
            self.detail_records = [record for record in self.detail_records if record[0] != int(values[0])]

        self.refresh_tabeloverzicht()


if __name__ == "__main__":
    root = tk.Tk()
    app = KostenBeheerApp(root)
    root.mainloop()