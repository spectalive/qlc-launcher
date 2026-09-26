# TODO

- [ ] **Clients find the show by themselves (from Vibra-Lab/vibra-lighting,
  2026-09-26).** Announce the running show over mDNS/Bonjour, and show a QR
  code with `http://ADDRESS:PORT/`, so a tablet or phone reaches it without
  typing an address. Smallest next step: register `_http._tcp` with
  `dns-sd -R` (or `NSNetService`) for the verified port once the HTTP check
  passes, and stop it with the child.
- [ ] **Choose the show at launch (from vibra-lighting, 2026-09-26).** Today a
  show is chosen at install time (`--workspace`, one app per `--name`).
  Smallest next step: decide whether a picker at launch is still wanted now
  that several named apps can be installed side by side.
- [ ] **A human Dock click and a visible notification banner have never been
  observed (2026-09-13).** Every verification ran `launch.py` or `open` from a
  shell. Smallest next step: click the Dock icon at the rig and note the
  banner.
