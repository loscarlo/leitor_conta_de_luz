import os
import PyPDF2
import re
import csv
import pandas as pd

# Define o caminho do arquivo CSV
arquivo_csv = "/Users/carloscarvalho/Downloads/first_dashboard_colunas_novas_tratado.csv"

# Load the CSV data into a DataFrame
df = pd.read_csv(arquivo_csv)


# Função para extrair e imprimir valores com base em um padrão de expressão regular
def extract(pattern, text):
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    else:
        return None


# Define regular expression patterns to find os valores de interesse
pattern_injetada = r'Energia injetada - ([\d\.,]+)'
pattern_creditos = r'Saldo de Créditos: ([\d\.,]+)'
pattern_total_pagar = r'CONSUMO FATURADO Nº DIAS FAT[\s\S]+?(\d+,\d+)'
pattern_preco_unitario = r'Energia Elétrica kWh kWh [\d\.]+ ([\d\.,]+)'
pattern_medidor = r'MEDIDOR: (\d+)'
pattern_data_emissao = r'DATA DE EMISSÃO: (\d{2}/\d{2}/\d{4})'
# pattern_injetada_tusd = r'Energia Injetada kWh - TUSD ([\d\.,]+)'
# pattern_injetada_gd_tusd = r'Energia Injetada GD kWh - TUSD ([\d\.,]+)'
pattern_injetada_cons = r'(?:Energia Injetada kWh - TUSD kWh|Energia Injetada GD kWh -TUSD kWh) (\d+)'  # r'(?:Energia Injetada kWh - TUSD kWh|Energia Injetada GD kWh - TUSD kWh) (\d+\.\d+)'

# Define o caminho da pasta contendo os arquivos PDF
pasta_contendo_pdfs = "/Users/carloscarvalho/Library/Mobile Documents/com~apple~CloudDocs/BKP/solar/contas de Luz UCs/FEV24"

# # Define o caminho do arquivo CSV
# arquivo_csv = "/Users/carloscarvalho/Downloads/first_dashboard_colunas_novas_tratado.csv"

# Lê todas as linhas do arquivo CSV
with open(arquivo_csv, 'r', newline='') as csv_file:
    reader = csv.reader(csv_file)
    linhas_existente = list(reader)

# Cria ou abre o arquivo CSV para escrita
with open(arquivo_csv, 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)

    # Escreve as linhas existentes
    writer.writerows(linhas_existente)

    # Itera sobre os arquivos na pasta
    for filename in os.listdir(pasta_contendo_pdfs):
        if filename.endswith(".pdf"):
            # Abre o arquivo PDF
            with open(os.path.join(pasta_contendo_pdfs, filename), 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""

                # Extrai texto de cada página do PDF
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    text += page_text

                # Extrai os valores de interesse
                valor_injetada = extract(pattern_injetada, text)
                saldo_creditos = extract(pattern_creditos, text)
                total_pagar = extract(pattern_total_pagar, text)
                preco_unitario = extract(pattern_preco_unitario, text)
                medidor = extract(pattern_medidor, text)
                data_de_emissao = extract(pattern_data_emissao, text)
                # valor_injetada_tusd = extract(pattern_injetada_tusd, text)
                # valor_injetada_gd_tusd = extract(pattern_injetada_gd_tusd, text)
                valor_injetada_cons = extract(pattern_injetada_cons, text)

                # Search for the line containing "Energia kWh Tarifa Convencional"
                lines = text.split('\n')
                consumo_faturado = None
                for line in lines:
                    if "Energia kWh Tarifa Convencional" in line:
                        # Extract the last three characters, which represent the consumption value
                        consumo_faturado = line[-3:].strip()
                        break

                # correlacionando numero do medidor com propritario da unidade
                unidade_cons = None
                if medidor == '7514336':
                    unidade_cons = 'Valdione'
                elif medidor == '8399344':
                    unidade_cons = 'Luciana'
                elif medidor == '10325865':
                    unidade_cons = 'Ju&Rafael'
                else:
                    unidade_cons = 'Carlos'

                # adequando a formatacao das variaveis:
                valor_injetada = float(valor_injetada.replace('.', '').replace(',', '.'))
                saldo_creditos = float(saldo_creditos.replace('.', '').replace(',', '.'))
                total_pagar = float(total_pagar.replace('.', '').replace(',', '.'))
                preco_unitario = float(preco_unitario)
                # medidor =
                # data_de_emissão =
                consumo_faturado = float(consumo_faturado.replace('.', '').replace(',', '.'))
                valor_injetada_cons = float(valor_injetada_cons)

                # substituindo zeros por '' p/ varlor_injetada (para coluna energia_gerada ficar sem zeros)
                if valor_injetada == 0:
                    valor_injetada = ''
                else:
                    valor_injetada = valor_injetada

                # criando campo calculado "credito_mes_unidade":
                saldo_credito_mes_ant_unidade = df[df['unidade'] == unidade_cons]['saldo_credito'].iloc[-1]
                credito_mes_unidade = saldo_creditos - saldo_credito_mes_ant_unidade

                # criando campo calculado "energia_inj":
                energia_inj_unidade = credito_mes_unidade + valor_injetada_cons

                # criando campo calculado "cota_unidade":
                # cota_unidade = energia_inj_unidade / valor_injetada(do Carlos)

                # Escreve os valores extraídos no arquivo CSV
                writer.writerow(
                    [data_de_emissao, unidade_cons, medidor, valor_injetada, consumo_faturado, saldo_creditos,
                     total_pagar, preco_unitario, energia_inj_unidade, credito_mes_unidade, valor_injetada_cons])

print("Valores extraídos e escritos no arquivo CSV com sucesso!")