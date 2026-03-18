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

### Modes de redémarrage

Options de Restart

- `no (défaut)` :	Ne redémarre jamais. Pour services one-shot, tâches ponctuelles...
- `on-success` :	Redémarre uniquement si le processus sort avec code 0. Pour les scripts qui doivent s'exécuter à nouveau après succès.
- `on-failure` :	Redémarre si exit code ≠ 0, signal, ou timeout (évite les boucles infinies).
- `on-abnormal` :	Redémarre sur signaux, timeout, watchdog. Pour les services critiques qui ne doivent pas planter silencieusement.
- `on-watchdog` :	Redémarre uniquement sur timeout watchdog. Pour les services avec surveillance matérielle/logicielle.
- `on-abort` :	Redémarre uniquement sur signaux (SIGTERM, SIGINT, etc.). Pour les services qui doivent survivre aux interruptions.
- `always` :	Redémarre dans tous les cas (redémarre même après CTRL-C).

### Autres paramètres utiles

```ini
[Service]
# Délai entre les redémarrages (évite les boucles rapides)
RestartSec=10

# Limite le nombre de redémarrages (optionnel)
StartLimitBurst=5
StartLimitIntervalSec=60

# Arrêt propre avec timeout
TimeoutStopSec=30

# Signaux envoyés à l'arrêt
KillSignal=SIGTERM
KillMode=mixed
```

## Recommandations Lumo

- **VLC** :	Assurez-vous que `python3-vlc` est installé et accessible.
- **Audio** :	Configurez la sortie audio par défaut dans `/boot/config.txt` si nécessaire.
- **Logs** :	Utilisez `journalctl -u vintageradio.service` pour déboguer.
- **Arrêt propre** :	Le service *systemd* gère le signal SIGTERM, mais votre code doit gérer SIGINT (CTRL-C).

