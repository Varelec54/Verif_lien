# Vérificateur de Liens Sécurisé (Interne & Externe) - `verif_lien.py`

`verif_lien.py` est une application de bureau légère développée en Python avec une interface graphique **Tkinter**. Elle permet de parcourir un site web de manière récursive pour auditer l'ensemble de ses liens, identifier les liens cassés (internes et externes) et suivre le déroulement de l'analyse en temps réel.

## 🚀 Fonctionnalités principales

- **Interface graphique intuitive :** Suivi en direct du crawling via un journal de bord (Logs) et centralisation des erreurs dans un rapport dédié.
- **Exploration récursive des pages internes :** Analyse automatique de toutes les pages d'un même domaine.
- **Vérification des liens externes :** Test du statut HTTP des liens sortants pointant vers d'autres domaines.
- **Simulation de navigateur réel :** Utilisation d'en-têtes HTTP (User-Agent, Accept, etc.) pour éviter les blocages de sécurité basiques lors des requêtes.
- **Gestion des threads :** L'interface reste fluide et réactive pendant toute la durée du scan grâce à l'utilisation de threads en arrière-plan.
- **Contrôle utilisateur :** Possibilité de stopper l'analyse à tout moment.

---

## 📋 Prérequis

L'application utilise uniquement la bibliothèque standard de Python. Aucun paquet externe (`pip`) n'est requis.

- **Python 3.x** installé sur votre machine.

---

## 🛠️ Utilisation

1. Téléchargez ou placez le fichier `verif_lien.py` sur votre poste.
2. Ouvrez un terminal ou une invite de commande dans le dossier du script.
3. Lancez l'application avec la commande suivante :
   ```bash
   python verif_lien.py
