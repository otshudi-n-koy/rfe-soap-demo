"""
Mock server SOAP — Webservice legacy de facturation RFE
Implémentation Flask/XML (compatible Python 3.12)
"""
from flask import Flask, request, Response
from datetime import datetime
import threading

app = Flask(__name__)

NAMESPACE = "http://legacy.intermarche.fr/facturation"

# ── État en mémoire ────────────────────────────────────────────────────────
factures_db = {}

# ── Helpers XML ────────────────────────────────────────────────────────────

def soap_response(body_content: str) -> Response:
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope
    xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:fac="{NAMESPACE}">
  <soapenv:Header/>
  <soapenv:Body>
    {body_content}
  </soapenv:Body>
</soapenv:Envelope>"""
    return Response(xml, status=200, mimetype="text/xml")


def soap_fault(code: str, message: str) -> Response:
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>
    <soapenv:Fault>
      <faultcode>{code}</faultcode>
      <faultstring>{message}</faultstring>
    </soapenv:Fault>
  </soapenv:Body>
</soapenv:Envelope>"""
    return Response(xml, status=500, mimetype="text/xml")


def extract_tag(xml_str: str, tag: str) -> str:
    import re
    pattern = rf"<(?:[^:>]+:)?{tag}[^>]*>(.*?)</(?:[^:>]+:)?{tag}>"
    match = re.search(pattern, xml_str, re.DOTALL)
    return match.group(1).strip() if match else ""


# ── WSDL ───────────────────────────────────────────────────────────────────

@app.route("/facturation", methods=["GET"])
def wsdl():
    import os
    wsdl_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "wsdl", "facturation_legacy.wsdl"
    )
    with open(wsdl_path, "r", encoding="utf-8") as f:
        content = f.read()
    return Response(content, status=200, mimetype="text/xml")


# ── Endpoint SOAP ──────────────────────────────────────────────────────────

@app.route("/facturation", methods=["POST"])
def soap_endpoint():
    body = request.data.decode("utf-8")
    action = request.headers.get("SOAPAction", "").strip('"')

    if "SoumettreFacture" in action or "SoumettreFacture" in body:
        return handle_soumettre_facture(body)
    elif "ConsulterStatut" in action or "ConsulterStatut" in body:
        return handle_consulter_statut(body)
    else:
        return soap_fault("UNKNOWN_OPERATION", "Opération inconnue")


def handle_soumettre_facture(body: str) -> Response:
    numero = extract_tag(body, "numeroFacture")
    siren_emetteur = extract_tag(body, "sirenEmetteur")
    siren_destinataire = extract_tag(body, "sirenDestinataire")
    montant_ht = extract_tag(body, "montantHT")
    taux_tva = extract_tag(body, "tauxTVA")
    montant_ttc = extract_tag(body, "montantTTC")
    devise = extract_tag(body, "devise") or "EUR"

    # Validation SIREN
    if siren_emetteur == "000000000":
        return soap_fault("INVALID_SIREN", "Le SIREN émetteur est invalide")

    # Validation TVA
    try:
        ht = float(montant_ht)
        tva = float(taux_tva)
        ttc = float(montant_ttc)
        expected = round(ht * (1 + tva / 100), 2)
        if abs(expected - ttc) > 0.01:
            return soap_fault("TVA_MISMATCH", f"Montant TTC incohérent — attendu {expected}")
    except (ValueError, TypeError):
        pass

    # Enregistrement
    date_reception = datetime.now().isoformat()
    factures_db[numero] = {
        "idFacture": numero,
        "statut": "SUBMITTED",
        "dateReception": date_reception,
        "sirenEmetteur": siren_emetteur,
        "sirenDestinataire": siren_destinataire,
    }

    print(f"  [SOAP] Facture soumise : {numero} → SUBMITTED")

    return soap_response(f"""
    <fac:SoumettreFactureResponse>
      <fac:idFacture>{numero}</fac:idFacture>
      <fac:statut>SUBMITTED</fac:statut>
      <fac:message>Facture reçue et enregistrée avec succès</fac:message>
      <fac:dateReception>{date_reception}</fac:dateReception>
    </fac:SoumettreFactureResponse>""")


def handle_consulter_statut(body: str) -> Response:
    id_facture = extract_tag(body, "idFacture")
    facture = factures_db.get(id_facture)

    if not facture:
        return soap_fault("INVOICE_NOT_FOUND", f"Facture {id_facture} introuvable")

    print(f"  [SOAP] Statut consulté : {id_facture} → {facture['statut']}")

    return soap_response(f"""
    <fac:ConsulterStatutResponse>
      <fac:idFacture>{facture['idFacture']}</fac:idFacture>
      <fac:statut>{facture['statut']}</fac:statut>
      <fac:dateModification>{datetime.now().isoformat()}</fac:dateModification>
    </fac:ConsulterStatutResponse>""")


# ── Lifecycle ──────────────────────────────────────────────────────────────

_server_thread = None


def start_soap_server(host="127.0.0.1", port=8002):
    global _server_thread
    _server_thread = threading.Thread(
        target=lambda: app.run(host=host, port=port, debug=False, use_reloader=False),
        daemon=True
    )
    _server_thread.start()
    print(f"  [SOAP] Mock server running on http://{host}:{port}/facturation")
    print(f"  [SOAP] WSDL disponible sur http://{host}:{port}/facturation?wsdl")


def stop_soap_server():
    print("  [SOAP] Server stopped")


def reset_soap_state():
    factures_db.clear()
    print("  [SOAP] État réinitialisé")