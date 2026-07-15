# rfe-soap-demo

> Tests webservices SOAP legacy — Réforme de la Facturation Électronique (RFE)  
> Python · pytest-bdd · Gherkin · Flask · Zeep · SoapUI

---

## Contexte

Ce projet démontre une approche de tests BDD sur les flux **SOAP legacy** dans le cadre de la RFE chez Intermarché. Les fournisseurs legacy (grands industriels, coopératives agricoles) exposent leurs systèmes de facturation via des webservices SOAP plutôt que des APIs REST.

---

## Stack technique

| Composant | Outil |
|-----------|-------|
| Langage | Python 3.12 |
| Framework BDD | pytest-bdd + Gherkin |
| Mock SOAP server | Flask + XML |
| Client SOAP | Zeep (lecture WSDL) |
| Contrat interface | WSDL |
| Tests manuels | SoapUI 5.7 |

---

## Structure

rfe-soap-demo/
├── wsdl/
│   └── facturation_legacy.wsdl          # Contrat SOAP (équivalent Swagger)
├── soapui/
│   └── RFE-Legacy-SoapUI-Project.xml    # Projet SoapUI importable
├── features/
│   └── soap/
│       └── facturation_soap.feature     # 5 scénarios BDD
├── src/
│   ├── mock/
│   │   └── soap_server.py               # Mock SOAP server (Flask)
│   ├── steps/
│   │   └── soap_steps.py                # Step definitions pytest-bdd
│   └── support/
│       └── soap_client.py               # Client SOAP (zeep)
├── tests/
│   └── test_soap.py                     # Test runner
├── conftest.py
├── requirements.txt
└── pytest.ini

---

## Lancement

```bash
pip install -r requirements.txt
pytest tests/ -v
```

Résultat attendu :
5 passed in 14s

---

## Projet SoapUI

Importer dans SoapUI Open Source :

1. File → Import Project
2. Sélectionner `soapui/RFE-Legacy-SoapUI-Project.xml`
3. Démarrer le mock server (`pytest tests/` lance automatiquement)
4. Lancer les test cases depuis SoapUI

---

**Auteur :** N'Koy OTSHUDI — QA Senior · ISTQB CTFL  
[github.com/otshudi-n-koy](https://github.com/otshudi-n-koy)
