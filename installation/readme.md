# Vintage Radio - Installation

## Démarrage automatique Raspberry

### Installation

- Copier le fichier dans `/etc/systemd/system/vintageradio.service`.

- S'assurer d'avoir la dernière version du programme (`git pull`).

### Activer et démarrer le service

```bash
# Recharger la configuration systemd
sudo systemctl daemon-reload

# Activer le démarrage automatique au boot
sudo systemctl enable vintageradio.service

# Démarrer immédiatement (optionnel)
sudo systemctl start vintageradio.service
```

### Vérifier le statut

```bash
# Voir si le service tourne
sudo systemctl status vintageradio.service

# Voir les logs
sudo journalctl -u vintageradio.service -f
```

### Arrêter/Démarrer le service manuellement

```bash
sudo systemctl stop vintageradio.service
sudo systemctl start vintageradio.service
sudo systemctl restart vintageradio.service
```


## Recommandations Lumo

- **VLC** :	Assurez-vous que `python3-vlc` est installé et accessible.
- **Audio** :	Configurez la sortie audio par défaut dans `/boot/config.txt` si nécessaire.
- **Logs** :	Utilisez `journalctl -u vintageradio.service` pour déboguer.
- **Arrêt propre** :	Le service *systemd* gère le signal SIGTERM, mais votre code doit gérer SIGINT (CTRL-C).

