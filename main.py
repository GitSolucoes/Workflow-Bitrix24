from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import time
import random
from datetime import datetime, timedelta, timezone
import logging

app = Flask(__name__)

# Load environment variables
load_dotenv()

BITRIX_URL = os.getenv('BITRIX_URL')


BITRIX_WEBHOOK_URL = f"{BITRIX_URL}/bizproc.workflow.start"



def make_request_with_retry(url, data, max_retries=3, retry_delay=5):
    """Faz a requisição e tenta novamente em caso de erro (404, 400, 500, etc.)."""
    for attempt in range(max_retries):
        try:
            print(f"🕒 Tentativa {attempt + 1} de {max_retries} para {url}")
            response = requests.post(url, json=data)
            
            # Verifica se a resposta tem status 200
            response.raise_for_status()
            
            print("✅ Requisição bem-sucedida!")
            return response  # Retorna a resposta se for bem-sucedida
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Erro na tentativa {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Aguardando {retry_delay} segundos antes de tentar novamente...")
                time.sleep(retry_delay)
            else:
                print("❌ Máximo de tentativas atingido. Falha na requisição.")
    return None  # Retorna None se todas as tentativas falharem





def update_card_bitrix(card_id, name_of_field, value):
    url = f"{BASE_URL_API_BITRIX}/{PROFILE}/{CODIGO_BITRIX}/crm.deal.update"
    data = {
        'id': card_id,
        'fields': {
            name_of_field: value
        }
    }
    if value is None:
        print('⚠️ A variável "value" está nula ⚠️')
        return -1

    response = make_request_with_retry(url, data)
    if response and response.status_code == 200:
        print(f"✅ Campo '{name_of_field}' atualizado com sucesso.")
        return True
    else:
        print("❌ Falha ao atualizar o campo.")
        if response is not None:
            print(response.text)
        return None





def convert_for_gmt_minus_3(date_from_bitrix):
    hour_obj = datetime.fromisoformat(date_from_bitrix)
    hour_sub = hour_obj - timedelta(hours=6)
    new_hour_formated = hour_sub.isoformat()
    return new_hour_formated
    
WORKFLOW_IDS = {
    "workflow1": "1196", #primeiro boleto(1.1)
    "workflow2": "1200", #primeiro boleto(1.2)
    "workflow3": "1204", #segundo boleto(1.1)
    "workflow4": "1206", #segundo boleto(1.2)
    "workflow5": "1208", #terceiro boleto(1.1)
    "workflow6": "1210", #terceiro boleto(1.2)
    "workflow7": "1212", #quarto boleto(1.1)
    "workflow8": "1214", #quarto boleto(1.2)
    "workflow9": "1216", #quinto boleto(1.1)
    "workflow10": "1218", #quinto boleto(1.2)
    "workflow11": "1314", #workflow para o site
    "workflow12": "1294", #workflow para a fila de ativos
    "workflow13": "1390", #workflow para campo sem fuso horario ser atualizado.
    "workflow14": "1426", #workflow que muda o campo de Relatorio data.
    "workflow15": "1428", #workflow que muda o campo de Relatorio data/hora.
    "workflow16": "1474",
    "workflowredeneutra": "1502",
    "workflowouro": "1496",
    "workflowpadrao": "1498",
    "workflowprata": "1500",
    "workflow_grafeno_75": "1682", # Planos oferta especial vero grafeno 75
    "workflow_grafeno_80": "1852", # Planos oferta especial vero grafeno 80
    "workflow_safira": "1854", # Planos oferta especial vero safira
    "workflowt1_a_t9": "1668",
    "workflowt10_t14": "1670",
    "workflowt_ALTOS_PARNAIBA_TERESINA": "1672",
    "workflowt_CIDADES_ESPECIAIS_1": "1674",
    "workflowt_CIDADES_ESPECIAIS_2": "1676",
    "workflowt_CIDADES_ESPECIAIS_3": "1678",
    "workflow_TELEFONEFIXO_T5_a_T7": "1680",
    "workflow_desktop_ferro": "1542",
    "workflow_desktop_bronze": "1540",
    "workflow_desktop_prata": "1544",
    "workflow_desktop_ouro": "1546",
    "workflow_desktop_platina": "1548",
    "workflow_desktop_diamante": "1550",
    "workflow_desktop_ascedente": "1552",
    "workflow_desktop_imortal": "1554",
    "workflow_blink": "1558",
    "workflow_tim": "1560",
    "workflow_algar": "1564",
    "workflow_algar_600MB": "1564",
    "workflow_algar_800MB": "1660",
    "workflow_algar_specialcities": "1666",
    "workflow_contactid": "1626",
    "workflow_phase": "1628",
    "workflow_vencimento": "1630",
    "workflow_saudademelhorfibra": "1652",
    "workflow_formatacao_nome_primeiro_boleto_vero": "1702",
    "workflow_cep-adress": "1744",
    "workflow_bl-fibra": "1856", # Planos BL FIBRA
    "utm": "1862" # Workflow teste de UTMS
}







@app.route('/webhook/<workflow_name>', methods=['POST'])
def start_workflow(workflow_name):
    print("✅ Webhook acionado!") 
    deal_id = request.args.get('deal_id')

    if not deal_id:
        return jsonify({"error": "deal_id não fornecido"}), 400

    workflow_id = WORKFLOW_IDS.get(workflow_name)
    if not workflow_id:
        return jsonify({"error": "Workflow não encontrado"}), 404

    array = ["crm", "CCrmDocumentDeal", f"DEAL_{deal_id}"]
    data = {"TEMPLATE_ID": workflow_id, "DOCUMENT_ID": array}

    response = make_request_with_retry(BITRIX_WEBHOOK_URL, data)
    if response is None:
        return jsonify({"error": "Todas as tentativas falharam", "details": "Verifique o log para mais informações"}), 500
    
    return jsonify(response.json()), response.status_code





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1475)
