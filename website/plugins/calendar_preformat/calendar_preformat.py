# -*- coding: utf-8 -*-

# Copyright © 2012-2013 Roberto Alsina

# Permission is hereby granted, free of charge, to any
# person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import doit
from doit.tools import run_once, result_dep
from datetime import datetime, timedelta
from dateutil.rrule import rrulestr, rruleset
import icalendar as ical
from pytz import UTC
import pytz
from babel.dates import format_datetime

from nikola.plugin_categories import Task
from nikola.utils import LOGGER, get_logger, LocaleBorg, TemplateHookRegistry

import requests


class CalendarPlugin(Task):

    name = "calendar_preformat"

    def gen_tasks(self):

        log_calendar = get_logger('log_calendar')

        url = self.site.config.get('CALENDAR_URL', None)
        log_calendar.info(url)

        def fetch_online_calendar(url = None):
            if url != None:
                ical = requests.request('GET', url)
                log_calendar.info("Downloaded")
                self.site.cache.set('events_ical',ical.text)


        def collect_events(days_in_past, days_in_future):
            cache_cal = self.site.cache.get('events_ical')
            cal = ical.Calendar.from_ical(cache_cal)

            events = []

            calc_startdate = datetime.now(tz=UTC)
            if days_in_past:
                calc_startdate -= timedelta(days=int(days_in_past))
            calc_enddate = datetime.now(tz=UTC)
            if days_in_future:
                calc_enddate += timedelta(days=int(days_in_future))

            for element in cal.walk():
                eventdict = {}
                if element.name == "VEVENT":
                    if element.get('summary') is not None:
                        eventdict['summary'] = element.get('summary')
                    if element.get('description') is not None:
                        eventdict['description'] = element.get('description')
                    if element.get('location') is not None:
                        eventdict['location'] = element.get('location')
                    if element.get('url') is not None:
                        eventdict['url'] = element.get('url')
                    if element.get('dtstart') is not None:
                        eventdict['dtstart'] = element.get('dtstart').dt
                    if element.get('dtend') is not None:
                        eventdict['dtend'] = element.get('dtend').dt
                    if element.get('x-lugfl-alwaysvisible') is not None:
                        eventdict['x-lugfl-alwaysvisible'] = True
                    else:
                        eventdict['x-lugfl-alwaysvisible'] = False

                    rules_text = '\n'.join([line for line in element.content_lines() if line.startswith('RRULE')])
                    if days_in_future is not None and rules_text:

                        # Build rrule to use for calculation if available
                        rules = rruleset()
                        first_rule = rrulestr(rules_text, dtstart=element.get('dtstart').dt)

                        # force UTC if no tzinfo is present in until part (bug in older iCal and Moz)
                        if first_rule._until and first_rule._until.tzinfo is None:
                            first_rule._until = first_rule._until.replace(tzinfo=UTC)
                        rules.rrule(first_rule)

                        # Also check for excluded dates in entry, has API list bug for single entry
                        exdates = element.get('exdate')
                        if not isinstance(exdates, list):
                            exdates = [exdates]
                        for exdate in exdates:
                            #doit.tools.set_trace()
                            try:
                                #rules.exdate(exdate.dts[0].dt)
                                pass
                            except AttributeError:  # skip empty entries
                                pass

                        for entry_calcdate in rules.between(calc_startdate, calc_enddate):
                            tzname = entry_calcdate.tzinfo.zone
                            entry_calcdate = entry_calcdate.replace(tzinfo=None)
                            timezone = pytz.timezone(tzname)
                            entry_calcdate = timezone.localize(entry_calcdate)

                            new_entry = eventdict.copy()
                            duration = new_entry['dtend'] - new_entry['dtstart']
                            new_entry['dtstart'] = entry_calcdate
                            new_entry['dtend'] = entry_calcdate + duration
                            events.append(new_entry)
                    if days_in_future is not None:
                        if days_in_past is not None and eventdict['dtstart'] > calc_startdate and (
                                eventdict['dtstart'] < calc_enddate or eventdict['x-lugfl-alwaysvisible']):
                            events.append(eventdict)
                        elif days_in_past is None and eventdict['dtstart'] < calc_enddate or eventdict['x-lugfl-alwaysvisible']:
                            events.append(eventdict)
                    else:
                        events.append(eventdict)

            log_calendar.info("collect_events finished")
            return events

        def generate_calendar_list(timezone_name, days_in_past, days_in_future):
            template = 'calendar_preformat.tmpl'
            deps = self.site.template_system.template_deps(template)

            events = collect_events(days_in_past, days_in_future)
            self.site._GLOBAL_CONTEXT['events'] = sorted(events, key=lambda k: k['dtstart'])
            log_calendar.info("generate_calendar_list finished")

        # File to read VEVENTS from
        calendar_url = self.site.config.get('CALENDAR_URL',None)
        calendar_filename = self.site.config.get('CALENDAR_FILENAME', None)
        calendar_days_in_past = self.site.config.get('CALENDAR_DAYS_IN_PAST', 0)
        calendar_days_in_future = self.site.config.get('CALENDAR_DAYS_IN_FUTURE', 90)
        calendar_output_filename = self.site.config.get('CALENDAR_OUTPUT_FILENAME', 'calendar_preformat.tmpl')

        timezone_name = self.site.config.get('TIMEZONE')

        yield {
            'basename': 'calendar_preformat',
            'name': 'calendar_download',
            'actions': [
                (fetch_online_calendar,[url])
            ],
            'uptodate': [False],
        }
        # Yield a task for Doit
        if calendar_url is not None:
            yield {
                'basename': 'calendar_preformat',
                'name': 'generate_calendar_list',
                'actions': [
                    (generate_calendar_list, [timezone_name, calendar_days_in_past, calendar_days_in_future])
                ],
                'uptodate': [False],
            }
        else:
            yield self.group_task()
