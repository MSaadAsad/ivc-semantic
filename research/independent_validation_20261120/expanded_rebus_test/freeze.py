"""Freeze all six source panels before scoring; never imports dictionary data."""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[2]
sys.path.insert(0, str(REPO / 'work_scripts'))
import key2a_rebus_lock as engine

# Human translations of source concept lists, not fitted to Elamite matches.
# Umlauts are written in the normalization used by the existing gloss cleaner.
GERMAN = {
'fixed48': '''
740:krug|topf|gefass:haus|heim|wohnung|familie|sippe
700:schale|topf|hohl:mass|kapazitat
400:kamm|entwirren:klein|wenig|jung
220:fisch:stern|gestirn|sternbild
520:speer|lanze|pfeil:hauptling|herrscher|konig|held
390:baum|pflanze|strauch:nahen|sticken|weben|flechten
861:auge|sicht|sehen:gewicht|bruchteil|eigentum|besitz
820:rad|wagen:viertel|bein|fuss
320:stufe|treppe|leiter:ration|mass|zulage|kapazitat|gewicht
590:korb|flechten|zopf:sack|last|ballen|bundel
615:weber|webstuhl|rohr:feld|rucken|land|beet
705:dreschen|feld|boden:schiff|gefass|boot
176:sitzen|bleiben|wohnen:steuer|tribut|abgabe|zahlung
090:mann|mannlich|gatte|diener:herrschen|verwalten|kontrollieren
233:riss|spalten|bersten:morgenrote|tagesanbruch|morgen|tag
415:gabel|zinke|zweig:ergreifen|fassen|fangen|kontrollieren
920:mond:monat
407:zweig:stoff|weber
806:stengel|stiel:hirse|getreide
798:muschel|schale:binden|knupfen|bauen|haus
255:krokodil:erste|anfang|haupt|kapital
840:paar|ehepaar:verbinden|vereinigen|vereinigung|ubereinstimmen
760:spross|trieb|ranke:jung|kind|saugling
368:fahne|banner:geben|gewahren
690:binden|knupfen|befestigen:bundel|paket|gebaude|lager
550:taille|mitte|zentrum:bezirk|land|provinz|ort
892:bogen:verkaufen|verkauf|preis
140:mutter|frau|matrone:gottin
154:tragstange|stange|joch:wachen|wachter|bewahren|schutzen|obdach
142:stab|stock|stange:schmied|eisen
503:berg|hugel:kranz|halskette
440:ecke|winkel|gasse:gefass|topf|pfanne|becher
435:haken|stachel:diener|wachter|begleiter|bote
845:linie|streifen|strich|zeichnen|schreiben:steuer|abgabe|zoll
850:auge|sicht:kupfer|bronze|kupferschmied
717:fuss|fussspur:diener|sklave|knechtschaft
413:getreide|reis|ahre:steuer|abgabe|schneiden|ernten
350:zaun|hof|pferch|gehege:wachter|diener|bote
460:trieb|zweig:kranz|girlande|halsband
482:berg|hugel:konig|kaiser|hauptling|fuhrung
480:spitze|scharf:gefass|kapazitat|mass
335:rahmen:topf|gefass|pfanne
540:trommel:mass|kapazitat
630:kafig|stall|nest|pferch|bienenstock:versammeln|verbinden|lagern|gelagert|zusammen
171:hangen|aufhangen|hangend:wiegen|gewicht|gleichgewicht|waage
831:klinge|waffe|pfeil|weber:getreide|reis
165:biegen|kurve|buckel|schnecke:kessel
104:springen|hupfen|schreiten|tanzen:sammeln|erheben|zuruckgewinnen
''',
'key4b30': '''
700:becher|schale|gefass|topf|krug|hohl:mass|kapazitat|getreide|ration|zulage|anteil
240:schnurrhaar|flosse|flugel|feder|wange|borste:stern|hell|scheinen|glitzern|hauptling|herr|perle
861:auge|samen|kern|knospe|raute|sicht:gewicht|bruchteil|anteil|eigentum|tribut|opfer
060:schrag|neigung|biegen|gebogen|kurve|krumm|lehnen: innen|inner|innerhalb|verbinden|vereinigen|viertel|gehoren
590:kasten|truhe|kiste|korb|flechten|zopf:sack|packen|ballen|bundel|speicher|lager|schatzkammer
741:krug|topf|wasserkrug|kanne|gefass:haus|bezirk|familie|wohnung|sippe|mieter
615:gitter|netz|maschen|rahmen|rohr|quadrat:feld|land|acker|rucken|gut|parzelle|hof
817:auge|samen|kern|knospe|raute|sicht:kasten|truhe|kiste|ladung|fracht|gewicht|anteil
233:spalten|halbieren|teilen|schneiden|scheibe|riss:stern|hell|scheinen|morgenrote|licht|glanz|sonne
415:gabel|zweig|zinke|rechen|verzweigen:ergreifen|fassen|kontrollieren|anteil|pacht|hauptling|herr
920:mond|sichel|mondformig|bogen:monat|jahreszeit|zeitraum|amt|handwerk|perle
405:baum|zweig|ast|strauch:faden|garn|schnur|weben|stricken|spinnen
407:baum|zweig|ast|horn|strauch:stoff|textil|kleid|gewebe|farbe|weber
806:blatt|stengel|stiel|spross|trieb|zweig:ernte|hirse|getreide|ertrag|erzeugnis|gerste
798:blatt|blutenblatt|zange|klaue|krabbe:haus|palast|hof|sippe|kaufmann|erbe
255:tier|bestie|fisch|vogel|geflugel|flosse:ration|zulage|getreide|speicher|hauptling|konig|ausgabe
803:blatt|blatter|laub|blutenblatt:haus|wohnung|heim|familie|sippe
156:tragen|last|trager|schulter|stange|joch:ballen|packen|sack|bundel|ration|mass|gewicht
840:paar|zwilling|doppelt|blatt|blatter:gleich|passen|ubereinstimmen|verbinden|vereinigen|armreif|ring|prufung
760:spross|trieb|knospe|zweig|ranke:kind|jung|sohn|nachkomme|erbe
368:fahne|banner|wimpel|kriechpflanze|flugel:geben|gewahren|zuteilen|titel|abstammung|getreide|ration
690:knoten|knupfen|binden|befestigen|klammer|glied:bundel|paket|lager|gebaude|ration|getreide|pfand
550:mund|kiefer|zange|schnabel|klaue:tor|portal|tur|eingang|zitadelle|festung|bezirk
892:bogen|pfeil|bogenschutze:verkaufen|verkauf|preis|kosten|wert|handel|kaufmann
140:frau|weiblich|brust|mutter|matrone|madchen:gottin|konigin|herrscher|hauptling|heilig|tempel|zitadelle
151:tragen|last|trager|stange|schulter:wachen|schutzen|wachter|obdach|verteidigung|bewahren
142:stab|stock|stange|zepter|keule:konig|hauptling|herrscher|herr|souveran|beamter
503:hugel|berg|gipfel|rucken|haufen:kranz|halskette|schnur|perle|muschel|farbe|gut
231:durchbohren|stechen|pflanzen|stock|linie|strich:stern|hell|scheinen|land|bezirk|gut|stier
706:becher|schale|gefass|topf|krug|hohl:mass|scheffel|kapazitat|getreide|elfenbein|elefant
''',
'key5a13': '''
240:strahl|balken|flosse|widerhaken|schrag|neigen:stern|hell|scheinen|gluhen|glanz|licht
060:schrag|neigung|biegen|kurve|krumm|lehnen:innen|innerhalb|gehoren|abhangen|verbinden|inneres
798:krabbe|muschel|zange|klaue:ergreifen|fassen|halten|binden|haus|gilde
550:taille|mitte|zentrum|eng|kneifen|drucken:land|bezirk|provinz|zitadelle|ort
142:stab|stock|stange|zauberstab|keule:mass|regel|grenze|messen|konig|herrscher
440:ecke|winkel|nische|krumme|ellbogen:topf|gefass|pokal|becher|krug|irden
692:kreuz|kreuzen|quer|kreuzweise:versammlung|rat|gilde|amt|zitadelle|bezirk
435:haken|zinke|gabel|pflock|stachel|widerhaken:verbundeter|gefahrte|hauptling|stutze|diener|stellvertreter
585:zelt|baldachin|markise|schirm|dach|giebel:tempel|palast|zitadelle|heiligtum|halle|werkstatt
595:streifen|stange|kasten|quadrat|draht:ofen|schmiede|brennofen|kupfer|schmelzen
845:linie|strich|streifen|schraffur|zeichnen|furche:steuer|abgabe|zoll|erheben|pacht
527:querbalken|riegel|klinke|planke|tafel|scharnier:tur|tor|portal|eingang|schwelle|gehege
416:gabel|zweig|zinke|rechen:seehafen|hafen|furt|ergreifen|fassen
''',
'key6a24': '''
142:stab|stock|stange|zauberstab|keule:schmied|eisen|kupfer|mass|regel|grenze
692:kreuz|kreuzen|diagonal|gitter:versammlung|rat|zitadelle|bezirk|amt|palast
585:schirm|sonnenschirm|baldachin|zelt|dach|giebel:zitadelle|palast|tempel|garnison|werkstatt|heiligtum
595:streifen|linie|strich|schraffur|zeichnen:steuer|abgabe|zoll|erheben|kupfer
527:riegel|klinke|querbalken|planke|scharnier:tor|tur|festung|bezirk|grenze|wachter
388:banyan|pipal|feige|blatt|laub:konig|koniglich|steuer|stoff|ware
384:banyan|pipal|feige|blatt|laub:gut|zuteilen|kupfer|sippe|abstammung
350:stall|krippe|zaun|egge|rechen:dorf|pflug|herde|vieh|weide|hof
455:flugel|schwanz|feder|schmetterling:stern|hell|siegel|gold|handel
460:trieb|spross|dorn|strauch|stachel:kranz|girlande|halskette|opfer|heilig
482:berg|hugel|gipfel|scharfe|spitze:kaiser|konig|herr|fuhrung|speicher|ablagerung
070:pfosten|saule|arm|statue:prufung|rechnung|zeuge|hauptling|richter
480:spitze|scharf|keil|kegel|gipfel:gefass|mass|kapazitat|gewicht|kupfer|barren
335:trog|becken|rahmen|doppelt|gestell:gefass|korb|getreide|ration|mass|speicher
540:trommel|tamburin|sanduhr|fliege:kapazitat|mass|topf|gefass|krug|behalter
645:kreuz|kreuzen|schere|diagonal:gewicht|gold|munze|gleichgewicht|bronze|axt
621:zimmer|kammer|wohnung|fenster|laden:siegel|titel|hauptling|herrscher|amt|wachter
630:vogelkafig|stall|kafig|pferch|nest|bienenstock:versammeln|verbinden|lagern|speicher|depot|werkzeug
877:blute|blume|blutenblatt|diamant:juwel|perle|gold|gewicht|anteil
171:hangen|aufhangen|schwingen|joch|pendel:gewicht|standard|gleichgewicht|waage|stein|gleich
297:glanz|pracht|sonne|strahl|funke:gewicht|anteil|steuer|viertel|gold|preis
831:klinge|flugel|feder|federkiel|federbusch:reis|getreide|kaufmann|handel|verkaufen|schiff
165:biegen|kurve|buckel|schnecke|spirale:kessel|kupfer|gefass|topf|monat
104:springen|hupfen|schreiten|tanzen:sammeln|erheben|steuer|ware|zuteilen|stoff
'''}

def terms_regex(terms):
    return r'\b(?:' + '|'.join(re.escape(t.strip()) for t in terms if t.strip()) + r')\b'

def translations(panel):
    rows = [line.strip().split(':') for line in GERMAN[panel].strip().splitlines()]
    return {s: (a.split('|'), b.split('|')) for s, a, b in rows}

def main():
    panels = {}
    paths = ['research/independent_validation_20261120/ivc_language_test/claims.json',
             'work_scripts/key2a_rebus_lock.py', 'work_data/sem/sign_anchors.csv',
             'work_data/lang_m2/signs.csv', 'work_data/key6a/master_lexicon_after_key6a.csv']
    claims = json.loads((REPO / paths[0]).read_text())['claims']
    tr = translations('fixed48')
    panels['fixed48'] = [dict(sign=c['sign'], title=c['title'],
        a_en=terms_regex(c['a']), b_en=terms_regex(c['b']),
        a_de=terms_regex(tr[c['sign']][0]), b_de=terms_regex(tr[c['sign']][1]),
        source=paths[0]) for c in claims if c['kind'] in ('bridge', 'polysemy')]
    for name, pairs in [('auto51', engine.build_auto_tier1_pairs(engine.ALL_SOURCE_DOMAINS)),
                        ('legacy12', engine.CLEAN_WAVE2B_12)]:
        panels[name] = [dict(sign=s, title=t, a_en=a, a_de=ad, b_en=b, b_de=bd,
                             source='work_scripts/key2a_rebus_lock.py')
                        for s, t, a, ad, b, bd in pairs]
    for name, path in [('key4b30','work_data/key4b/test4b1_top30_sign_table.csv'),
                       ('key5a13','work_data/key5a/trackA_per_sign_bridges.csv'),
                       ('key6a24','work_data/key6a/trackA_per_sign_bridges.csv')]:
        paths.append(path)
        tr = translations(name)
        panels[name] = []
        for r in csv.DictReader((REPO / path).open()):
            s = r['sign']
            panels[name].append(dict(sign=s, title=r['domainA_en']+' → '+r['domainB_en'],
                a_en=terms_regex(r['domainA_en'].split(',')),
                b_en=terms_regex(r['domainB_en'].split(',')),
                a_de=terms_regex(tr[s][0]), b_de=terms_regex(tr[s][1]), source=path))
    assert {k: len(v) for k, v in panels.items()} == dict(fixed48=48, auto51=51,
        legacy12=12, key4b30=30, key5a13=13, key6a24=24)
    obj = dict(plan_sha256=hashlib.sha256((BASE/'PLAN.md').read_bytes()).hexdigest(),
               input_sha256={p:hashlib.sha256((REPO/p).read_bytes()).hexdigest() for p in paths},
               panels=panels, note='Frozen before expanded scoring; not human-blinded or preregistered.')
    (BASE / 'cases.json').write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')
    # Master coverage is a ledger, not additional statistically independent trials.
    (BASE/'results').mkdir(exist_ok=True)
    rows = []
    for r in csv.DictReader((REPO/'work_data/key6a/master_lexicon_after_key6a.csv').open()):
        represented = [p for p, cases in panels.items() if any(c['sign']==r['sign'] for c in cases)]
        rows.append(dict(**r, panels='; '.join(represented),
                         scope='paired concepts supplied by source' if represented else
                         'not separately scored: numeral/literal/compound/allograph or no frozen two-sided pair'))
    with (BASE/'results/master_scope.csv').open('w') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n');w.writeheader();w.writerows(rows)
    print({k:len(v) for k,v in panels.items()}, 'master rows', len(rows))

if __name__ == '__main__':
    main()
