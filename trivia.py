# coding=utf-8
"""Trivia module"""
# Copyright 2016 Hery Eugene

import re, json, sqlite3, time, os
from datetime import datetime, timedelta

import sopel.module
from sopel.module import rule, event, priority, thread, example
from sopel.tools import stderr, Identifier, events

STRINGS = {
    'mg': {
        'EFA_MANDEHA': u'\x0300,01Efa mandeha ny lalao natombok\'i %s!',
        'NANOMBOKA': u'\x0300,01 Nanomboka ny lalao i %s',
        'NIJANONA': u'\x0300,01 Najanon\'i %s ny lalao.',
        'FANONTANIANA': u'\x02Fanontaniana :\x0F %s',
        'FANONTANIANA_DISO': u'Tsy ara-dalàna ny fanontaniana voaray fa avereno indray ny !lalao',
        'VALINY_TSY_METY': u'Tsy ara-dalàna ny valim-panontaniana voaray ka avereno indray',
        'TORO_1': u'\x02\x0303Fanoroana 1 :\x03\x0F %s (litera %s)',
        'TORO_2': u'\x02\x0303Fanoroana 2 :\x03\x0F %s',
        'TORO_3': u'\x02\x0303Fanoroana 3 :\x03\x0F %s',
        'VALINY': u'Ny valiny dia: \x02\x0304%s\x03\x0F',
        'VALINY_MARINA': u'\x0303MARINA\x03, \x02\x0304%s\x03\x0F no nahita ny valiny <\x02%s\x0F> tao anatin\'ny \x02%s\x0F segondra ary nahazo isa \x02%s\x0F. Ny isa azony androany dia \x02%s\x0F',
        'NAHAZO_ISA': u'Nahazo isa \x02%s\x0F',
        'ISA_AZO_ANDROANY': u'Isa azony androany dia ',
        'TSISY': u'mbola sy nisy',
        'FILAHARANA': u'Ny voalohany nandritra ny herinandro dia i \x02%s\x0F nahazo isa \x02\x0304%s\x03\x0F, nandritra ity volana ity dia i \x02%s\x0F, nahazo isa \x02\x0304%s\x03\x0F, nandritra ny taona dia i \x02%s\x0F, nahazo isa \x02\x0304%s\x03\x0F, ary hatramin\'izay dia i \x02%s\x0F, nahazo isa \x02\x0304%s\x03\x0F',
        'FIARAHABANA': u'Tonga soa eto amin\'ny lalao, efa natombok\'i \x02%s\x0F ny lalao. Afaka mandray anjara ianao.',
        'HANOMBOKA_LALAO': u'Tonga soa eto amin\'ny lalao. Raha hanomboka lalao dia soraty hoe \x02%s\x0F. Raha mila fanampiana dia \x02%s\x0F',
        'FILAZANA': u'Efa mandeha ny lalao. Raha te handray anjara dia soraty hoe \x02/join %s ',
        'ISA_HATRIZAY': u'Ny isa azon\'i \x02%s\x0F nandritra ny herinandro: \x02\x0304%s\x03\x0F, ny volana: \x02\x0304%s\x03\x0F, ny taona: \x02\x0304%s\x03\x0F, hatrizay: \x02\x0304%s\x03\x0F.',
        'TSY_MANANA_ISA': u'Mbola tsy manana isa voatahiry i %s',
        'FANOROANA': {
            u'Ireo baiko miasa :',
            u'!top : Ireo namana voalohany',
            u'!place : Ny isa azonao voatahiry',
            u'!top10 : Ny mpilalao 10 voalohany',
            u'!stop : Ajanona ny lalao',
            u'!start : Atomboka ny lalao',
        },
        'VOALOHANY_HERINANDRO': u'Ny voalohany nandritra ny herinandro dia \x02%s\x0F nahazo isa \x02\x0304%s\x03\x0F',
        'VOALOHANY_VOLANA': u'Ny voalohany nandritra ny volana dia \x02%s\x0F nahazo isa \x02\x0304%s\x03\x0F',
        'VOALOHANY_TAONA': u'Ny voalohany nandritra ny taona dia \x02%s\x0F nahazo isa \x02\x0304%s\x03\x0F',
        'VOALOHANY_HATRIZAY': u'Ny voalohany hatrizay kosa dia \x02%s\x0F nahazo isa \x02\x0304%s\x03\x0F',
        'FOLO_VOALOHANY_HATRIZAY': u'Ireo mpilalao folo voalohany hatrizay',
        'LAHARANA_FAHA': u'#%s \x02%s\x0F nahazo isa \x02\x0304%s\x03\x0F',

    },
    'fr': {
        'EFA_MANDEHA': u'\x0300,01Le quizz a déjà été commencé par %s!',
        'NANOMBOKA': u'\x0300,01 Quizz commencé par %s \x03',
        'NIJANONA': u'\x0300,01 Quizz arreté par %s. \x03',
        'FANONTANIANA': u'\x02Question :\x0F %s',
        'FANONTANIANA_DISO': u'La question n\'est pas valide',
        'VALINY_TSY_METY': u'La réponse n\'est pas valide.',
        'TORO_1': u'\x02\x0303Suggestion 1 :\x03\x0F %s (%s lettres)',
        'TORO_2': u'\x02\x0303Suggestion 2 :\x03\x0F %s',
        'TORO_3': u'\x02\x0303Suggestion 3 :\x03\x0F %s',
        'VALINY': u'La réponse est: \x02\x0304%s\x03\x0F',
        'VALINY_MARINA': u'\x0303EXACT\x03, \x02\x0304%s\x03\x0F a trouvé la bonne réponse <\x02%s\x0F> en \x02%s\x0F secondes avec \x02%s\x0F points. Son score d\'aujourd\'hui est de \x02%s\x0F points.',
        'NAHAZO_ISA': u'Points \x02%s\x0F',
        'ISA_AZO_ANDROANY': u'Ses points pour aujourd\'hui ',
        'TSISY': u'encore vide',
        'FILAHARANA': u'Premier cette semaine \x02%s\x0F avec \x02\x0304%s\x03\x0F points, durant ce mois \x02%s\x0F, avec \x02\x0304%s\x03\x0F points, premier de l\'année \x02%s\x0F, avec \x02\x0304%s\x03\x0F points, et depuis le commencement: \x02%s\x0F, avec \x02\x0304%s\x03\x0F points',
        'FIARAHABANA': u'Bienvenue sur le salon, \x02%s\x0F a déjà commencé le quizz. Tu peux y participer tout de suite.',
        'HANOMBOKA_LALAO': u'Bienvenue sur le salon. Pour commencer le quizz utilise \x02%s\x0F. Si tu as besoin d\'aide utilise la commande \x02%s\x0F',
        'FILAZANA': u'Le jeu du quizz est disponible. Pour jouer joindre le canal avec \x02/join %s',
        'ISA_HATRIZAY': u'Les points gagnés par \x02%s\x0F cette semaine: \x02\x0304%s\x03\x0F, ce mois: \x02\x0304%s\x03\x0F, cette année: \x02\x0304%s\x03\x0F, depuis le debut: \x02\x0304%s\x03\x0F.',
        'TSY_MANANA_ISA': u'%s n\'a pas encore de statistique dans la base de données.',
        'FANOROANA': {u'Commandes utilisées :',
                      u'!top : Les premiers rangs',
                      u'!place : Tes points',
                      u'!top10 : Les dix premiers joueurs',
                      u'!stop : Arreter le jeu',
                      u'!start : Commencer le jeu',
                      },
        'VOALOHANY_HERINANDRO': u'Le top 1 de la semaine est  \x02%s\x0F avec \x02\x0304%s\x03\x0F points',
        'VOALOHANY_VOLANA': u'Le top 1 du mois est  \x02%s\x0F avec \x02\x0304%s\x03\x0F points',
        'VOALOHANY_TAONA': u'Le top 1 de l\'année est  \x02%s\x0F avec \x02\x0304%s\x03\x0F points',
        'VOALOHANY_HATRIZAY': u'Le top 1 depuis le debut est  \x02%s\x0F avec \x02\x0304%s\x03\x0F points',
        'FOLO_VOALOHANY_HATRIZAY': u'Les 10 premiers joueurs de tous les temps: ',
        'LAHARANA_FAHA': u'#%s \x02%s\x0F avec \x02\x0304%s\x03\x0F points',

    }

}

with open(os.path.dirname(os.path.realpath(__file__)) + '/config.json') as json_data_file:
    config = json.load(json_data_file)

start_command = config.setdefault("start_command", "!start")
stop_command = config.setdefault("stop_command", "!stop")
help_command = config.setdefault("help_command", "!aide")

lang = config.setdefault("language", "mg")
config['room'] = config.setdefault("room", "#trivia")
TENY = STRINGS[lang]


class Trivia():
    def __init__(self):
        self.nanomboka = False  # Efa nanomboka ve ny lalao?
        self.mpanomboka = ""  # Iza no nanomboka azy?
        self.mandeha = dict()  # Ny Fanontaniana mipetraka am'zao
        self.mpilalao = dict()  # Array misy ny mpilalao
        self.filaharana = dict()  # fitehirizana ny ambony indrindra
        self.faharetany = 30  # fanoroana interval
        self.sala = 100  # point par level
        # Ny point azo dia zaraina amin'ny fotoana lasa
        # connect to database
        self.toerana = dict()
        self.dingana = 1
        self.showstat = 1

    def start(self, bot, trigger):
        if trigger.sender != config['room']:
            return
        if self.nanomboka:
            bot.say(TENY['EFA_MANDEHA'] % self.mpanomboka)
            return
        bot.say(TENY['NANOMBOKA'] % trigger.nick)
        self.mpanomboka = trigger.nick
        self.nanomboka = True

        while self.nanomboka:
            self.play(bot, trigger)

    def play(self, bot, trigger):

        rows = self.getrows("SELECT fanontaniana, valiny, haavo from lalao ORDER BY Random()")
        if len(rows) > 0:
            self.mandeha = rows[0]

        fanontaniana = self.mandeha[0]

        self.point = self.sala * self.mandeha[2]
        if fanontaniana == "":
            bot.say(TENY['FANONTANIANA_DISO'])
            self.stop(bot, trigger)
            return
        if self.mandeha[1] == "":
            bot.say(TENY['VALINY_TSY_METY'])
            self.stop(bot, trigger)
            return

        bot.say(TENY['FANONTANIANA'] % fanontaniana)
        self.daty_nanombohana = datetime.now()

        # fanoroana 1
        fanoroana = "|"
        i = 0
        for c in self.mandeha[1]:
            if c == " ":
                fanoroana += "   |"
            else:
                fanoroana += "_|"
        bot.say(TENY['TORO_1'] % (fanoroana, len(self.mandeha[1])))

        time.sleep(self.faharetany / 3)
        if len(self.mandeha) == 0:
            return

        # fanoroana 2
        if len(self.mandeha[1]) > 4:
            fanoroana = "|"
            i = 0
            for c in self.mandeha[1]:
                if i % 4 == 0:
                    fanoroana += "\x0304" + c + "\x03|"
                elif c == " ":
                    fanoroana += "   |"
                else:
                    fanoroana += "_|"
                i += 1
            bot.say(TENY['TORO_2'] % fanoroana)

        time.sleep(self.faharetany / 3)

        if len(self.mandeha) == 0:
            return

        # fanoroana 3
        if len(self.mandeha[1]) > 2:
            fanoroana = "|"
            i = 0
            for c in self.mandeha[1]:
                if i % 2 == 0:
                    fanoroana += "\x0304" + c + "\x03|"
                elif c == " ":
                    fanoroana += "   |"
                else:
                    fanoroana += "_|"
                i += 1
            bot.say(TENY['TORO_3'] % fanoroana)

        time.sleep(self.faharetany / 4)

        # display answer

        if len(self.mandeha) == 0:
            return
        bot.say(TENY['VALINY'] % self.mandeha[1])
        self.mandeha = dict()

    def execute(self, *args, **kwargs):
        """Execute an arbitrary SQL query against the database.

                Returns a cursor object, on which things like `.fetchall()` can be
                called per PEP 249."""
        retry_count = 0
        conn = None
        while not conn and retry_count <= 10:
            # If there is trouble reading the file, retry for 10 attempts
            # then just give up...
            try:
                conn = sqlite3.connect(config['trivia_db'])
            except sqlite3.OperationalError:
                retry_count += 1
                time.sleep(0.001)

        if not conn and retry_count > 10:
            raise sqlite3.OperationalError("Can't connect to sqlite database.")
        cur = conn.cursor()
        cur.execute(*args, **kwargs)
        conn.commit()
        conn.close()

    def getrows(self, *args, **kwargs):

        retry_count = 0
        conn = None
        while not conn and retry_count <= 10:
            # If there is trouble reading the file, retry for 10 attempts
            # then just give up...
            try:
                conn = sqlite3.connect(config['trivia_db'])
            except sqlite3.OperationalError:
                retry_count += 1
                time.sleep(0.001)

        if not conn and retry_count > 10:
            raise sqlite3.OperationalError("Can't connect to sqlite database.")


        cur = conn.cursor()
        ret = cur.execute(*args, **kwargs)
        rows = ret.fetchall()
        conn.close()

        return rows

    def stop(self, bot, trigger):
        if trigger.sender != config['room']:
            return
        if trigger.admin or self.mpanomboka == trigger.nick:
            self.mandeha = {}
            self.nanomboka = False
            self.mpanomboka = ""
            bot.say(TENY['NIJANONA'] % trigger.nick)


    def hamarino(self, x, y):
        if (x.lower() == y.lower()):
            return True

    def reply(self, bot, trigger):
        if trigger.sender != config['room']:
            return
        if not self.mandeha:
            return
        if len(self.mandeha) > 0 and self.mandeha[1]:
            if self.hamarino(trigger.args[1], self.mandeha[1]):  # marina
                self.play_stop_time = datetime.now()
                # tonga dia ajanony ny fanontaniana
                valiny = self.mandeha[1];
                self.mandeha = dict()

                duration = self.play_stop_time - self.daty_nanombohana

                self.point = self.point - ((duration.seconds * 100) / self.faharetany)
                combined = duration.seconds + duration.microseconds / 1E6
                if trigger.nick not in self.mpilalao:
                    self.mpilalao[trigger.nick] = {
                        'niditra': datetime.now(),
                        'isa': 0,
                    }
                if not self.mpilalao[trigger.nick]['isa']:
                    self.mpilalao[trigger.nick]['isa'] = 0
                totaly = self.mpilalao[trigger.nick]['isa'] + self.point
                bot.say(
                    TENY['VALINY_MARINA'] % (trigger.nick, valiny, "%.2f" % combined, self.point, totaly))
                # omeo point

                daty = datetime.now()
                self.mpilalao[trigger.nick]['isa'] = totaly
                self.execute("INSERT INTO mpilalao (nick, isa, daty) VALUES (?, ?, ?)",
                             [trigger.nick, self.point, daty])

                self.display_stats(bot, config['room'])

    def display_stats(self, bot, room):
        # Karazana stats disponibles
        if self.showstat == 1:
            # Top
            self.say_top(bot, room)
            self.showstat = 2
        else:
            # top10
            self.say_top10(bot, room)
            self.showstat = 1

    def join(self, bot, trigger):
        if trigger.sender != config['room'] or trigger.nick == bot.nick:
            return

        # tehirizina amin'ny array users

        sasakalina = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        rows = self.getrows("SELECT SUM(isa) FROM mpilalao WHERE nick = ? AND daty > ?",
                              [trigger.nick, sasakalina])



        if len(rows) > 0:
            totaly = rows[0]
            isa = totaly[0]
        else:
            isa = 0
        self.mpilalao[trigger.nick] = {
            'niditra': datetime.now(),
            'isa': isa
        }

        # andefasana hafatra momba ny lalao
        if len(self.mandeha) > 0:
            bot.notice(TENY['FIARAHABANA'] % self.mpanomboka, trigger.nick)
        else:
            bot.notice(TENY['HANOMBOKA_LALAO'] % (start_command, help_command), trigger.nick)

    def names(self, bot, trigger):
        """
            Alaina ny users rehetra
            """
        channels = re.search('(#\S*)', trigger.raw)
        if not channels:
            return
        channel = Identifier(channels.group(1))
        if channel != config['room']:
            return

        names = trigger.split()
        for name in names:
            name = re.sub(r'^[\+\%\@\&\~]', "", name)
            self.mpilalao[name] = {
                'niditra': datetime.now(),
                'isa': 0,
            }
        # fenoina avy any amin'ny db ny users array
        sasakalina = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        totaly = self.getrows("SELECT nick, SUM(isa) FROM mpilalao WHERE daty > ? GROUP BY nick",
                              [sasakalina])
        for total in totaly:
            if total[0] in self.mpilalao:
                self.mpilalao[total[0]]['isa'] = total[1]

    def stats(self, bot):
        if config['room'] in bot.channels:

            if self.dingana < 2:
                # weekly
                alatsinainy = datetime.today() - timedelta(days=datetime.today().weekday())
                alatsinainy = alatsinainy.replace(hour=0, minute=0, second=0)

                rows = self.getrows("SELECT nick, SUM(isa) FROM mpilalao WHERE daty > ? GROUP BY nick",
                                    [alatsinainy])
                for row in rows:
                    if row[0] in self.mpilalao:
                        self.mpilalao[row[0]]['herinandro'] = row[1]
                        self.update_stats_table('herinandro', row[0], row[1])
                self.dingana = 2
            elif self.dingana < 3:
                # monthly
                volana = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                rows = self.getrows("SELECT nick, SUM(isa) FROM mpilalao WHERE daty > ? GROUP BY nick",
                                    [volana])
                for row in rows:
                    if row[0] in self.mpilalao:
                        self.mpilalao[row[0]]['volana'] = row[1]
                        self.update_stats_table('volana', row[0], row[1])
                self.dingana = 3
            elif self.dingana < 4:
                # yearly
                taona = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                rows = self.getrows("SELECT nick, SUM(isa) FROM mpilalao WHERE daty > ? GROUP BY nick",
                                    [taona])
                for row in rows:
                    if row[0] in self.mpilalao:
                        self.mpilalao[row[0]]['taona'] = row[1]
                        self.update_stats_table('taona', row[0], row[1])
                self.dingana = 4
            elif self.dingana < 5:
                # overall
                rows = self.getrows("SELECT nick, SUM(isa) FROM mpilalao GROUP BY nick")
                for row in rows:
                    if row[0] in self.mpilalao:
                        self.mpilalao[row[0]]['hatrizay'] = row[1]
                        self.update_stats_table('hatrizay', row[0], row[1])
                self.dingana = 1

    def update_stats_table(self, field, nick, value):
        user_exist = self.getrows("SELECT nick FROM statistika WHERE nick = ?", [nick])
        if len(user_exist) > 0:
            self.execute("UPDATE statistika SET " + field + " = ? WHERE nick = ?", [value, nick])
        else:
            self.execute("INSERT INTO statistika (nick, " + field + ") VALUES (?, ?)", [nick, value])

    def update_stats(self):
        self.filaharana['id'] = datetime.now() - timedelta(minutes=20)
        # alaina isan'ora fotsiny
        if id not in self.filaharana or self.filaharana['id'] < datetime.now() - timedelta(minutes=15):
            alatsinainy = datetime.today() - timedelta(days=datetime.today().weekday())
            alatsinainy = alatsinainy.replace(hour=0, minute=0, second=0)
            rows = self.getrows(
                "SELECT nick, SUM(isa) FROM mpilalao WHERE daty > ? GROUP BY nick ORDER BY SUM(isa) DESC LIMIT 10",
                [alatsinainy])

            self.filaharana['herinandro'] = rows

            volana = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            rows = self.getrows(
                "SELECT nick, SUM(isa) FROM mpilalao WHERE daty > ? GROUP BY nick  ORDER BY SUM(isa) DESC LIMIT 10",
                [volana])
            self.filaharana['volana'] = rows

            taona = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            rows = self.getrows(
                "SELECT nick, SUM(isa) FROM mpilalao WHERE daty > ? GROUP BY nick ORDER BY SUM(isa) DESC LIMIT 10",
                [taona])
            self.filaharana['taona'] = rows

            rows = self.getrows(
                "SELECT nick, SUM(isa) FROM mpilalao GROUP BY nick ORDER BY SUM(isa) DESC LIMIT 10")
            self.filaharana['hatrizay'] = rows

            self.filaharana['id'] = datetime.now()

    def say_top(self, bot, dest):
        self.update_stats()
        msg = ""
        if self.filaharana['herinandro'] != None and len(self.filaharana['herinandro']) > 0:
            
            msg += " - " + TENY['VOALOHANY_HERINANDRO'] % (
                self.filaharana['herinandro'][0][0], self.filaharana['herinandro'][0][1])

        if self.filaharana['volana'] != None and len(self.filaharana['volana']) > 0:
            msg += " - " + TENY['VOALOHANY_VOLANA'] % (self.filaharana['volana'][0][0], self.filaharana['volana'][0][1])

        if self.filaharana['taona'] != None and len(self.filaharana['taona']) > 0:
            msg += " - " + TENY['VOALOHANY_TAONA'] % (self.filaharana['taona'][0][0], self.filaharana['taona'][0][1])

        if self.filaharana['hatrizay'] != None and len(self.filaharana['hatrizay']) > 0:
            msg += " - " + TENY['VOALOHANY_HATRIZAY'] % (
            self.filaharana['hatrizay'][0][0], self.filaharana['hatrizay'][0][1])

        if len(msg) == 0:
            msg += " " + TENY['TSISY']
        bot.say(msg, dest)

    def top(self, bot, trigger):
        self.say_top(bot, trigger.nick)
        return

    def say_top10(self, bot, dest):
        self.update_stats()

        if self.filaharana['hatrizay'] != None:
            msg = TENY['FOLO_VOALOHANY_HATRIZAY']
            i = 1
            for user in self.filaharana['hatrizay']:
                msg += " " + TENY['LAHARANA_FAHA'] % (i, user[0], user[1])
                i += 1

            bot.say(msg, dest)

    def top10(self, bot, trigger):
        self.say_top10(bot, trigger.nick)
        return

    def place(self, bot, trigger, nick):
        
        if nick not in self.toerana:
            rows = self.getrows("SELECT nick, herinandro, volana, taona, hatrizay FROM statistika WHERE nick = ?",
                               [nick])

            if len(rows) == 0:
                self.toerana[nick] = [nick, 0, 0, 0, 0]
            else:
                row = rows[0]
                self.toerana[row[0]] = row

        # rehefa ao am'zay
        if nick in self.toerana:
            bot.say(TENY['ISA_HATRIZAY'] % (
                nick,
                self.toerana[nick][1],
                self.toerana[nick][2],
                self.toerana[nick][3],
                self.toerana[nick][4]
            ), trigger.nick)

        else:
            bot.say(TENY['TSY_MANANA_ISA'] % trigger.nick)
        return

    def aide(self, bot, trigger):
        for term in TENY['FANOROANA']:
            bot.say(term, trigger.nick)


tvb = Trivia()


@event('JOIN')
@rule(r'.*')
def lalao_join(bot, trigger):
    tvb.join(bot, trigger)


@rule(start_command + '$')
@example(start_command + ' raha hanomboka lalao')
def lalao_start(bot, trigger):
    tvb.start(bot, trigger)


@rule(stop_command + '$')
def lalao_stop(bot, trigger):
    tvb.stop(bot, trigger)


@rule('!top$')
def lalao_top(bot, trigger):
    tvb.top(bot, trigger)


@rule('!top10$')
def lalao_top10(bot, trigger):
    tvb.top10(bot, trigger)


@rule('!place\s?(.*)?\s?')
def lalao_place(bot, trigger):
    if not trigger.group(1):
        nick = trigger.nick
    else:
        nick = trigger.group(1).strip()
    print nick
    tvb.place(bot, trigger, nick)


@rule(help_command + '$')
def lalao_aide(bot, trigger):
    tvb.aide(bot, trigger)


@rule('^[^\!\.]')  # all but commands
@priority('low')
def lalao_reply(bot, trigger):
    tvb.reply(bot, trigger)


@rule('(.*)')  # valin'ny NAMES
@event(events.RPL_NAMREPLY)
@priority('high')
@thread(False)
def handle_names(bot, trigger):
    tvb.names(bot, trigger)


@sopel.module.interval(900)
def statistics(bot):
    tvb.stats(bot)


@sopel.module.interval(920)
def announce(bot):
    for channel in bot.channels:
        if channel != config['room']:
            bot.msg(channel, TENY['FILAZANA'] % config['room'])
