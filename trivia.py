# coding=utf-8
"""Trivia module"""
# Copyright 2016 Hery Eugene

import re
import sqlite3
import time
from datetime import datetime, timedelta

import sopel.module
from sopel.module import rule, event, priority, thread
from sopel.tools import Identifier, events

import config #you have to copy config.dist.py into config.py

TENY = {
    'EFA_MANDEHA': '\x0300,01Efa mandeha ny lalao natombok\'i %s!',
    'NANOMBOKA': '\x0300,01 Nanomboka ny lalao i %s',
    'NIJANONA': '\x0300,01 Najanon\'i %s ny lalao.',
    'FANONTANIANA': '\x02Fanontaniana :\x0F %s',
    'FANONTANIANA_DISO': 'Tsy ara-dalàna ny fanontaniana voaray fa avereno indray ny !lalao',
    'VALINY_TSY_METY': 'Tsy ara-dalàna ny valim-panontaniana voaray ka avereno indray',
    'TORO_1': '\x02\x0303Fanoroana 1 :\x03\x0F %s (litera %s)',
    'TORO_2': '\x02\x0303Fanoroana 2 :\x03\x0F %s',
    'TORO_3': '\x02\x0303Fanoroana 3 :\x03\x0F %s',
    'VALINY': 'Ny valiny dia: \x02\x0304%s\x03\x0F',
    'VALINY_MARINA': '\x0303MARINA\x03, \x02\x0304%s\x03\x0F no nahita ny valiny <\x02%s\x0F> tao anatin\'ny \x02%s\x0F segondra ary nahazo isa \x02%s\x0F. Ny isa azony androany dia \x02%s\x0F',
    'NAHAZO_ISA': 'Nahazo isa \x02%s\x0F',
    'ISA_AZO_ANDROANY': 'Isa azony androany dia ',
    'TSISY': 'mbola sy nisy',
    'FILAHARANA': 'Ny voalohany nandritra ny herinandro dia i \x02%s\x0F nahazo isa \x02\x0304%s\x03\x0F, nandritra ity volana ity dia i \x02%s\x0F, nahazo isa \x02\x0304%s\x03\x0F, nandritra ny taona dia i \x02%s\x0F, nahazo isa \x02\x0304%s\x03\x0F, ary hatramin\'izay dia i \x02%s\x0F, nahazo isa \x02\x0304%s\x03\x0F',
}


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
        self.angona = ANGONA
        self.dingana = 1

        self.filaharana = {
            'id': None,
            'herinandro': {
                'nick': TENY['TSISY'],
                'isa': 0
            },
            'volana': {
                'nick': TENY['TSISY'],
                'isa': 0
            },
            'taona': {
                'nick': TENY['TSISY'],
                'isa': 0
            },
            'hatrizay': {
                'nick': TENY['TSISY'],
                'isa': 0
            },
        }

    def start(self, bot, trigger):
        if trigger.sender != EFITRA:
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
        self.mandeha = self.execute("SELECT fanontaniana, valiny, haavo from lalao ORDER BY Random()").fetchone()
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

    def connect(self):
        """Return a raw database connection object."""
        return sqlite3.connect(self.angona)

    def execute(self, *args, **kwargs):
        """Execute an arbitrary SQL query against the database.

        Returns a cursor object, on which things like `.fetchall()` can be
        called per PEP 249."""
        with self.connect() as conn:
            cur = conn.cursor()
            return cur.execute(*args, **kwargs)

    def stop(self, bot, trigger):
        if trigger.sender != EFITRA:
            return
        if trigger.admin or self.nanomboka:
            self.mandeha = {}
            self.nanomboka = False
            self.mpanomboka = ""
            bot.say(TENY['NIJANONA'] % trigger.nick)

    def hamarino(self, x, y):
        if (x.lower() == y.lower()):
            return True

    def reply(self, bot, trigger):
        if trigger.sender != EFITRA:
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
                if not self.mpilalao[trigger.nick]:
                    self.mpilalao[trigger.nick] = {
                        'niditra': datetime.now(),
                        'isa': 0,
                    }
                totaly = self.mpilalao[trigger.nick]['isa'] + self.point
                bot.say(
                    TENY['VALINY_MARINA'] % (trigger.nick, valiny, "%.2f" % combined, self.point, totaly))
                # omeo point

                daty = datetime.now()
                self.mpilalao[trigger.nick]['isa'] = totaly
                self.execute("INSERT INTO mpilalao (nick, isa, daty) VALUES (?, ?, ?)",
                             [trigger.nick, self.point, daty])

                self.display_stats(bot, EFITRA)

    def join(self, bot, trigger):
        if trigger.sender != EFITRA or trigger.nick == bot.nick:
            return

        # tehirizina amin'ny array users

        sasakalina = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        totaly = self.execute("SELECT SUM(isa) FROM mpilalao WHERE nick = ? AND daty > ?",
                              [trigger.nick, sasakalina]).fetchone()

        if totaly:
            isa = totaly[0]
        if not isa:
            isa = 0
        self.mpilalao[trigger.nick] = {
            'niditra': datetime.now(),
            'isa': isa
        }

    def names(self, bot, trigger):
        """
            Alaina ny users rehetra
            """
        channels = re.search('(#\S*)', trigger.raw)
        if not channels:
            return
        channel = Identifier(channels.group(1))
        if channel != EFITRA:
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
        totaly = self.execute("SELECT id, nick, SUM(isa) FROM mpilalao WHERE daty > ? GROUP BY nick",
                              [sasakalina]).fetchall()
        for total in totaly:
            if total[0] in self.mpilalao:
                self.mpilalao[total[0]]['isa'] = total[1]

    def stats(self, bot):
        if EFITRA in bot.channels:

            if self.dingana < 2:
                # weekly
                alatsinainy = datetime.today() - timedelta(days=datetime.today().weekday())
                alatsinainy = alatsinainy.replace(hour=0, minute=0, second=0)

                rows = self.execute("SELECT nick, SUM(isa) FROM mpilalao WHERE daty > ? GROUP BY nick",
                                    [alatsinainy]).fetchall()
                for row in rows:
                    if row[0] in self.mpilalao:
                        self.mpilalao[row[0]]['herinandro'] = row[1]
                        self.updateStat('herinandro', row[0], row[1])
                self.dingana = 2
            elif self.dingana < 3:
                # monthly
                volana = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                rows = self.execute("SELECT nick, SUM(isa) FROM mpilalao WHERE daty > ? GROUP BY nick",
                                    [volana]).fetchall()
                for row in rows:
                    if row[0] in self.mpilalao:
                        self.mpilalao[row[0]]['volana'] = row[1]
                        self.updateStat('volana', row[0], row[1])
                self.dingana = 3
            elif self.dingana < 4:
                # yearly
                taona = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                rows = self.execute("SELECT nick, SUM(isa) FROM mpilalao WHERE daty > ? GROUP BY nick",
                                    [taona]).fetchall()
                for row in rows:
                    if row[0] in self.mpilalao:
                        self.mpilalao[row[0]]['taona'] = row[1]
                        self.updateStat('taona', row[0], row[1])
                self.dingana = 4
            elif self.dingana < 5:
                # overall
                rows = self.execute("SELECT nick, SUM(isa) FROM mpilalao GROUP BY nick").fetchall()
                for row in rows:
                    if row[0] in self.mpilalao:
                        self.mpilalao[row[0]]['hatrizay'] = row[1]
                        self.updateStat('hatrizay', row[0], row[1])
                self.dingana = 1

    def updateStat(self, field, nick, value):
        user_exist = self.execute("SELECT nick FROM statistika WHERE nick = ?", [nick]).fetchall()
        if len(user_exist) > 0:
            self.execute("UPDATE statistika SET " + field + " = ? WHERE nick = ?", [value, nick])
        else:
            self.execute("INSERT INTO statistika (nick, " + field + ") VALUES (?, ?)", [nick, value])

    def display_stats(self, bot, dest):
        # alaina isan'ora fotsiny
        if self.filaharana['id'] != datetime.now().hour:
            alatsinainy = datetime.today() - timedelta(days=datetime.today().weekday())
            alatsinainy = alatsinainy.replace(hour=0, minute=0, second=0)
            row = self.execute(
                "SELECT nick, SUM(isa) FROM mpilalao WHERE daty > ? GROUP BY nick ORDER BY SUM(isa) LIMIT 1",
                [alatsinainy]).fetchone()
            self.filaharana['herinandro']['nick'] = row[0]
            self.filaharana['herinandro']['isa'] = row[1]

            volana = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            row = self.execute(
                "SELECT nick, SUM(isa) FROM mpilalao WHERE daty > ? GROUP BY nick  ORDER BY SUM(isa) LIMIT 1",
                [volana]).fetchone()
            self.filaharana['volana']['nick'] = row[0]
            self.filaharana['volana']['isa'] = row[1]

            taona = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            row = self.execute(
                "SELECT nick, SUM(isa) FROM mpilalao WHERE daty > ? GROUP BY nick ORDER BY SUM(isa) LIMIT 1",
                [taona]).fetchone()
            self.filaharana['taona']['nick'] = row[0]
            self.filaharana['taona']['isa'] = row[1]

            row = self.execute("SELECT nick, SUM(isa) FROM mpilalao GROUP BY nick").fetchone()
            self.filaharana['hatrizay']['nick'] = row[0]
            self.filaharana['hatrizay']['isa'] = row[1]

            self.filaharana['id'] = datetime.now().day

            bot.say(TENY['FILAHARANA'] % (
                self.filaharana['herinandro']['nick'],
                self.filaharana['herinandro']['isa'],
                self.filaharana['volana']['nick'],
                self.filaharana['volana']['isa'],
                self.filaharana['taona']['nick'],
                self.filaharana['taona']['isa'],
                self.filaharana['hatrizay']['nick'],
                self.filaharana['hatrizay']['isa'],
            ), dest)

    def top(self, bot, trigger):
        self.display_stats(bot, trigger.nick)


tvb = Trivia()


@event('JOIN')
@rule(r'.*')
def lalao_join(bot, trigger):
    tvb.join(bot, trigger)


@rule('!lalao$')
def lalao_start(bot, trigger):
    tvb.start(bot, trigger)


@rule('!stop$')
def lalao_stop(bot, trigger):
    tvb.stop(bot, trigger)


@rule('!top$')
def lalao_top(bot, trigger):
    tvb.top(bot, trigger)


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
