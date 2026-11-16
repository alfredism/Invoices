import os
import re
import csv
from shutil import copyfile
import shutil
from pypdf import PdfReader
import pandas as pd

# Configuration
invoices_dir = r"C:\Users\Lenovo\Mi unidad (alfredo.ismael7@gmail.com)\invoices\Mercadona"
#invoices_dir = r"C:\Antigravity\Pre_invoices"
output_dir = r"C:\output\invoices"
backup_output_dir = r"C:\output\invoices\bkup"
output_md_path = os.path.join(output_dir, "invoices_summary.md")
output_csv_path = os.path.join(output_dir, "invoices_summary.csv")
output_sortcsv_path = os.path.join(output_dir, "invoices_summary_sorted.csv")
files_summary_path = os.path.join(output_dir, "invoices_files_summary.csv")

def categorize_item(description):
    desc = description.lower()

    # Pienso Bruce
    if any(x in desc for x in ["C POLLO TER F Y V", "C.TERNERA/POLLO/VERD"]):
        return "Pienso"
    # Conservas
    if any(x in desc for x in ["fte. caballa",  "rabas", "anchoa", "anchoas", "mejillones escabeche", "mej. chile", "a.rellenas", 
                                "acie. rellenas", "aceituna", "almeja blanca", "filete melva", "maiz dulce", "mejillón", "paté", "pate", "sofreir",
                                "sardina ahumada", "sardinas", "sardinillas", "tom. receta", "verduras asadas", "zamburiña", "atún", "atun oliva", 
                                "tomate triturado", "tomate troceado", "tomate frito", "tomate entero", "chipirones rellenos", "almejones", "hueva de maruca"]):
        return "Conservas"

    # Congelados
    if any(x in desc for x in ["croqueta",  "rabas", "salteado", "delicias mar", "kebab", "arroz ultracongelado", "arroz vaporizado", "cookie dough",
                                "dochi", "gnocchi", "espinaca picada", "cong", "fresi pink", "habas baby", "michirones", "helado", "horchata", "menestra", "surimi",
                                "pata pulpo", "rabanitos", "salteado", "tempura verduras", "turrón", "vainilla praline", "wok verduras", "delicias",
                                "lagrimitas", "patatas gajo", "gambón empanado", "langostino rebozado", "langostino torpedo", "tequeños", "bravas"]):
        return "Congelados"
    
    # Hogar / Cuidado Personal
    if any(x in desc for x in ["vela", "spray", "limpiador", "deo", "insecticida", "desod", "esponja", "desmaq", 
                               "servilleta", "higienico", "higiénico", "champu", "champú", "crema anticelulitica", "articular", 
                               "memory", "valeriana", "balsamo", "bálsamo", "interdental", "laca",  "colágeno", "colageno", "lips", 
                               "alcohol", "amoniaco", "anticelulítico", "antipolillas", "basura", "borrador", "cabello y uñas",
                               "cáp.", "capsulas", "cápsulas", "vitamina", "fairy", "friegasuelos", "fosforos", "gel", "guante", "reductor", "jabon", "lejia",
                               "magnesio", "maquillaje", "mascara", "percarbonato", "perlas", "perf", "plumero", "quitagrasa", "encias", "encías",
                               "rollo cocina", "serum", "stick", "suavizante", "vitalift", "volumizer", "bolsa", "bolsas", "contra", "cubo",
                               "det blanca", "fibra blanca", "alcalina", "pulidor", "detergente", "esencia", "esparadrapo", "locion", "loción",
                               "papel", "toall"]):
        return "Home / Personal Care"
    
    # Servicio / Parking
    if "parking" in desc:
        return "Parking"
        
    # Infusiones
    if any(x in desc for x in ["arbol del te", "árbol del té", "chia", "infusion", "rooibos", "té", "te verde"]):
        return "Infusiones"

    # Pastas / Pizza
    if any(x in desc for x in ["tortell",  "pizza ", "lasagna", "lasaña", "macarrones", "spaghetti", "espagueti", "helices", "lasaña", 
                                "mac-cheese", "macarron", "noodles", "penne", "spaguetti", "ravioli", "ñoquis", "hojaldre"]):
        return "Pizza / Pastas"
        
    # Carne y Aves
    if any(x in desc for x in ["pollo", "huevos", "pechuga", "lomo", "bacon", "carrillada", "burger", "secreto", "alas", "jamon", "jamón", "pavo", 
                               "ternera", "longaniza", "paleta", "brocheta", "pluma", "chorizo", "compango", "cabeza", "cabez", "butifarra", "carpaccio",
                               "chopped", "codillo", "cost", "costilla", "entrecot", "york", "medallón", "pato", "muslo", "nuggets", "pelotas", "pelota",
                               "pincho", "sangre", "sobrasada", "solomillo", "fiambre", "pech", "carrillera", "cecina", "chistorra", "hamb. cerdo"]):
        return "Meat / Poultry"
        
    # Bebidas
    if any(x in desc for x in ["cerveza", "bebida", "cafe", "café", "agua ", "coca-cola", "cola", "aceite ", "caldo cocido", "gazpacho", "sopa", "vinagre", "vino",
                                "zumo fresco", "salmorejo"]):
        return "Drinks"

    # Cremas / Salsas
    if any(x in desc for x in ["crema calabaza", "crema de calabaza", "caldo", "crema queso", "crema setas", "allioli", "salsa", "yak soja"]):
        return "Cremas / Salsas"

    # Especias
    if any(x in desc for x in ["cayena", "cominos", "chía", "cola de caballo", "jengibre", "semillas", "orégano", "pimenton", "pimienta", "pimieta",
                               "sal de frutas", "sazonador", "topping", "canela"]):
        return "Especias"
        
    # Snacks, Dulces, Frutos Secos
    if any(x in desc for x in ["dulces", "caramel", "altramuces", "golosinas", "digestive", "almendra", "castaña", "castañas", "cocktail", 
                               "crunchy", "avena", "galleta", "choc", "moras", "pastilla", "nachos", "maiz frito", "maíz frito", "sacarina", 
                               "stevia", "azúcaritos", "gildas", "barrita", "bizcocho", "bombón", "bombon", "bombones", "c. eucalipto", "c. tostado",
                               "digest", "fresa-pastel", "gall.", "guindilla", "hummus", "masa", "encurtidos", "pi. calabaza", "pipas", "cacao",
                               "pringles", "torrezno", "torta", "tortita", "tortitas", "gilda", "pikotas", "snack", "xuxes", "patatas light",
                               "patatas campestres", "chili lima", "patatas serrano", "maiz frito", "patata queso", "chicle", "pat. classicas"]):
        return "Snacks / Sweets"
        
    # Panadería / Comida Preparada
    if any(x in desc for x in ["coca", "focaccia", "pan", "integral", "espelta", "trigo espelta", "chapata", "tortilla", "ensaladilla", "pure", "puré", 
                               "yakisoba", "gyoza",  "gnocchi", "pisto", "fritada",  "panecillo", "hogaza", "roscón", "roscon", "barra", "canelones",
                               "cereales solubles", "crackers", "ensalad americana", "ensalada", "migas", "napolitana", "poke", "regaña", "sandwich", "croissants",
                               "integrales", "bambú", "pan", "empanada", "capricho de yema", "wok"]):
        return "Bakery / Prepared Food"
    
    # Lácteos / Queso
    if any(x in desc for x in ["queso", "q. ", "q ", "gorgonzola", "roquefort", "brie", "yogur", "kefir", "kéfir", "natilla", "leche", 
                                "clara liquida", "+prot", "+ prote", "bif", "bíf", "flan", "gouda", "griego", "margarina", "mayonesa", "nata", "petit",
                                "q.fresco", "soja vainilla", "yog. nat", "cremoso", "grana padano", "mini tierno"]):
        return "Dairy / Cheese"
    
    # Legunbres / Arroz
    if any(x in desc for x in ["alubias", "alubia", "arroz j.sendra", "arroz sabroz", "garbanzos", "garbanzo", "lentejas", "lenteja", "harina", "la cigala"]):
        return "Legumbres / Arroz"
    
    # Pescado y Marisco
    if any(x in desc for x in ["pescado", "dorada", "caballa", "pescadilla", "langostino", "gambon", "gambón", "gamba", "chipiron", "berberecho", "navajas", "salmón",
                               "camarón"]):
        return "Fish / Seafood"

    # Verduras y Frutas
    if any(x in desc for x in ["tomate", "platano", "alcachofa", "plátano", "cebolla", "patata", "ajo", "brocoli", "brócoli", "pimiento",
                                "pepino", "banana", "coliflor", "romana", "champiñon", "champiñón", "cogollos", "coles de bruselas", "fresón", "guacamole", "kaki",
                                "piña", "seta", "t.cherry", "zanahoria", "apio", "cocido", "vegetales", "aguacate", "arreglo puchero", "berenjena", "brevas", "dátil",
                                "fresa", "mora"]):
        return "Vegetables / Fruit"
            
    return "Other / Grocery"

def parse_pdf_invoice(filepath):
    filename = os.path.basename(filepath)
    reader = PdfReader(filepath)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
    
    # 1. Invoice sent by (e.g. MERCADONA, S.A.)
    sent_by = "MERCADONA, S.A."
    if "MERCADONA, S.A." in full_text:
        sent_by = "MERCADONA, S.A."
    elif "MERCADONA" in full_text:
        sent_by = "MERCADONA"
    
    # 2. Date / Due Date in format YYYY/MM/DD
    date_match = re.search(r"(\d{2}/\d{2}/\d{4})", full_text)
    invoice_date = date_match.group(1) if date_match else "Unknown"
    df = pd.to_datetime(invoice_date, format="%d/%m/%Y", errors='coerce')
    due_date = df.strftime("%Y%m%d")


    # 3. Total amount
    total_match = re.search(r"TOTAL\s*(?:\(€\))?\s*(\d+,\d{2})", full_text, re.IGNORECASE)
    total_amount = "Unknown"
    if total_match:
        total_amount = total_match.group(1).replace(",", ".")
    
    # 4. Line Items
    items = []
    
    # Extract the items block
    lines = full_text.splitlines()
    start_idx = -1
    end_idx = -1
    
    for idx, line in enumerate(lines):
        if "Descripción" in line and "Importe" in line:
            start_idx = idx + 1
        elif "TOTAL" in line and start_idx != -1:
            end_idx = idx
            break
            
    if start_idx != -1 and end_idx != -1:
        items_lines = lines[start_idx:end_idx]
    else:
        items_lines = []
        
    pending_description = ""
    
    for line in items_lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for weight line
        weight_match = re.match(r"^(\d+,\d+)\s*kg\s*(\d+,\d+)\s*€/kg\s*(\d+,\d+)$", line)
        if weight_match:
            qty = weight_match.group(1).replace(",", ".") + " kg"
            price_unit = weight_match.group(2).replace(",", ".")
            amount = weight_match.group(3).replace(",", ".")
            
            desc = pending_description.strip() if pending_description else "Unknown weighted item"
            items.append({
                "quantity": qty,
                "description": desc,
                "price_unit": price_unit,
                "amount": amount
            })
            pending_description = ""
            continue
            
        # Check for standard item line
        item_match = re.match(r"^(\d+)\s+(.+?)(?:\s+(\d+,\d{2}))?(?:\s+(\d+,\d{2}))?$", line)
        if item_match:
            qty = item_match.group(1)
            desc = item_match.group(2)
            p1 = item_match.group(3)
            p2 = item_match.group(4)
            
            if p1 is None and p2 is None:
                pending_description = desc
            else:
                if p2 is None:
                    price_unit = p1.replace(",", ".")
                    amount = p1.replace(",", ".")
                else:
                    price_unit = p1.replace(",", ".")
                    amount = p2.replace(",", ".")
                
                items.append({
                    "quantity": qty,
                    "description": desc,
                    "price_unit": price_unit,
                    "amount": amount
                })
                pending_description = ""
            continue
            
        if "ENTRADA" in line and "SALIDA" in line:
            continue
            
        if pending_description:
            pending_description += " - " + line
        else:
            pending_description = line
            
    return {
        "filename": filename,
        "sent_by": sent_by,
        "due_date": due_date,
        "total_amount": total_amount,
        "items": items
    }

def find_and_parse_new_files(processed_files):
        
    # 2. Find and parse only new files

    new_data = []
    for filename in sorted(os.listdir(invoices_dir)):
        if filename.endswith(".pdf"):
            if filename in processed_files:
                print(f"Skipping already processed file: {filename}")
                continue
                
            filepath = os.path.join(invoices_dir, filename)
            print(f"Parsing new file: {filename}...")
            try:
                data = parse_pdf_invoice(filepath)
                new_data.append(data)
                print(f"  Successfully parsed {len(data['items'])} items. Total: {data['total_amount']}")
            except Exception as e:
                print(f"  Error parsing {filename}: {e}")
                
    return new_data

def format_and_append_to_csv(new_data, csv_exists):

    # 3. Format and append new items to CSV General Summary

    csv_rows = []
    if not csv_exists:
        # Write header first if CSV did not exist
        csv_rows.append(["Invoice Source", "Invoice Sent By", "Due Date", "Quantity", "Description", "Group of Items", "Price per Unit", "Amount"])
        
    for invoice in new_data:
        source_file = invoice["filename"]
        sent_by = invoice["sent_by"]
        due_date = invoice["due_date"]
        
        for item in invoice["items"]:
            category = categorize_item(item["description"])
            row = [
                source_file,
                sent_by,
                due_date,
                item["quantity"],
                item["description"],
                category,
                item["price_unit"],
                item["amount"]
            ]
            csv_rows.append(row)
            
    csv_mode = "a" if csv_exists else "w"
    with open(output_csv_path, csv_mode, newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(csv_rows)
    print(f"Appended {len(csv_rows)} rows to CSV summary at {output_csv_path}")

def format_and_append_to_files_summary(new_data, files_summary_exists):
    # 4. Format and append new files to CSV Files Summary
    files_summary_rows = []
    if not files_summary_exists:
        # Write header first if CSV did not exist
        files_summary_rows.append(["Invoice Source", "Invoice Sent By", "Due Date", "Total Amount"])
        
    for invoice in new_data:
        source_file = invoice["filename"]
        sent_by = invoice["sent_by"]
        due_date = invoice["due_date"]
        total_amount = invoice["total_amount"]
        
        row = [
            source_file,
            sent_by,
            due_date,
            total_amount
        ]
        files_summary_rows.append(row)
            
    files_summary_mode = "a" if files_summary_exists else "w"
    with open(files_summary_path, files_summary_mode, newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(files_summary_rows)
    print(f"Appended {len(files_summary_rows)} rows to Files Summary CSV at {files_summary_path}")

def read_processed_files(files_summary_exists):
    # 1. Read already processed files from CSV if it exists

    processed_files = set()

    if files_summary_exists:
        try:
            with open(files_summary_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                try:
                    source_idx = header.index("Invoice Source")
                    #count=0
                    for row in reader:
                        if row:
                            processed_files.add(row[source_idx])
                            #count+=1
                            #print("Este es el source index: {} y el count es: {}".format(row[source_idx], count))
                except ValueError:
                    print("Error: Could not find 'Invoice Source' column in existing CSV. Processing all files.")
                    files_summary_exists = False
        except Exception as e:
            print(f"Error reading existing CSV: {e}. Processing all files.")
            files_summary_exists = False
            
    print(f"Already processed files: {len(processed_files)}")

    return processed_files

def format_and_append_to_md(new_data, md_exists):

    # 5. Format and append new items to Markdown file

    md_lines = []        
    if not md_exists:
        md_lines.append("# New Invoices Summary Table")
        md_lines.append("")
        md_lines.append("| Invoice Source | Invoice Sent By | Due Date | Quantity | Description | Group of Items | Price per Unit (€) | Amount (€) |")
        md_lines.append("|---|---|---|---|---|---|---|---|---|")
        
    for invoice in new_data:
        source_file = invoice["filename"]
        sent_by = invoice["sent_by"]
        due_date = invoice["due_date"]
        
        for item in invoice["items"]:
            category = categorize_item(item["description"])
            md_lines.append(f"| {source_file} | {sent_by} | {due_date} | {item['quantity']} | {item['description']} | {category} | {item['price_unit']} | {item['amount']} |")
            
    md_mode = "a" if md_exists else "w"
    with open(output_md_path, md_mode, encoding="utf-8") as f:
        if md_exists:
            f.write("\n")
        f.write("\n".join(md_lines) + "\n")
    print(f"Appended markdown rows to summary at {output_md_path}")

def sort_csv_summary():
    # 4. Sort the CSV summary by Group of items, Description and then by Due Date
        
    df = pd.read_csv(output_csv_path)
    df_sort = df.sort_values(by=["Group of Items", "Description", "Due Date"], axis=0, ascending=[True, True, False], inplace=False)
    df_sort.to_csv(output_sortcsv_path, mode='w', index=False)
    
    print(f"Sorted CSV summary by Group of Items, Description, and Due Date at {output_sortcsv_path}")

def backup_all_output_files(csv_exists, files_summary_exists, md_exists, sortcsv_exists):
    # 0. Backup all the current output files to the backup folder if they exist
    # The name of the bkup files will have the extension of the date of the backup in the format YYYYMMDD

    today = pd.Timestamp.now().strftime("%Y%m%d")
    
    output_csv_path_bkup = os.path.join(backup_output_dir, f"invoices_summary_{today}.csv")
    output_sortcsv_path_bkup = os.path.join(backup_output_dir, f"invoices_summary_sorted_{today}.csv")
    files_summary_path_bkup = os.path.join(backup_output_dir, f"invoices_files_summary_{today}.csv")
    output_md_path_bkup = os.path.join(backup_output_dir, f"invoices_summary_{today}.md")
    print("Copying bkup files to {} - {} - {} - {}".format(output_csv_path_bkup, output_sortcsv_path_bkup, files_summary_path_bkup, output_md_path_bkup))

    if csv_exists:
        shutil.copyfile(output_csv_path, output_csv_path_bkup)
    if files_summary_exists:    
        shutil.copyfile(files_summary_path, files_summary_path_bkup)
    if md_exists:
        shutil.copyfile(output_md_path, output_md_path_bkup)
    if sortcsv_exists:
        shutil.copyfile(output_sortcsv_path, output_sortcsv_path_bkup)
     

def main():
    print("Starting incremental invoice parsing with grouping...")
        
    csv_exists = os.path.exists(output_csv_path)
    files_summary_exists = os.path.exists(files_summary_path)
    md_exists = os.path.exists(output_md_path)
    sortcsv_exists = os.path.exists(output_sortcsv_path)

    # 1. Read already processed files from CSV if it exists

    processed_files = read_processed_files(files_summary_exists)
        
    # 2. Find and parse only new files

    new_data = find_and_parse_new_files(processed_files)
            
    # 3. Check if there are new data to process, if not, exit the program. If yes, continue with the rest of the steps.

    if not new_data:
        print("No new invoice files found to process.")
        return

    # 4. Before starting writing the output files, backup all the current output files to the backup folder if they exist
        
    backup_all_output_files(csv_exists, files_summary_exists, md_exists, sortcsv_exists) 

    # 5. Format and append new items to CSV General Summary

    format_and_append_to_csv(new_data, csv_exists)

    # 6. Sort the CSV summary by Group of items, Description and then by Due Date

    sort_csv_summary()

    # 7. Format and append new files to CSV Files Summary
    
    format_and_append_to_files_summary(new_data, files_summary_exists)

    # 8. Format and append new items to Markdown file

    format_and_append_to_md(new_data, md_exists)

if __name__ == "__main__":
    main()
