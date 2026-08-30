"""Zeugen des Clients — laufen auf dem Host, nicht im Server-Behaelter.

Das Server-Abbild kennt `client/` nicht und traegt kein GTK; auf dem Host ist
beides da. Aufruf aus `novaberg/client`:

    python3 -m unittest discover -s tests -t .
"""
