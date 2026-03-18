# Vintage Radio - Tips


## Q&A - Problématiques rencontrées

### pynput requires a graphical display (X server) to capture keyboard input

- On peut remplacer `pyinput` par `termios` and `tty`. OK en mode console, mais ne fonctionne plus sous Windows.
- Il faut implémenter du cross-platform.
   - option 1 : conditionnal imports (Uses only built-in Python modules)
   - option 2 : librairie cross-platfom `readchar`
   Lumo recommande l'option 1 dans notre cas.


### PyCharm ne redirige pas les touches vers l'app

Aller dans le menu `Run -> Edit Configuration -> Modify options` et cocher **Emulate terminal in output console**.


### Raspberry: pas d'echo sur le terminal SSH

Tapez ceci pour rétablir le mode normal sur le terminal bloqué:

```
stty sane
```
