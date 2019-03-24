# -*- coding: utf-8 -*-

# Copyright © 2016 Roberto Alsina and others

# This plugin is based on the Pelican ical plugin
# available at https://github.com/getpelican/pelican-plugins/tree/master/ical
#
# This plugin is licensed under the
# GNU AFFERO GENERAL PUBLIC LICENSE Version 3
# according to the license guidelines from the Pelican plugin repo
#
# Original code is written by:
#
# Julien Ortet: https://github.com/cozo
# Justin Mayer: https://github.com/justinmayer
# calfzhou: https://github.com/calfzhou

from __future__ import print_function

import doit
from datetime import datetime, timedelta
from dateutil.rrule import rrulestr, rruleset
import icalendar as ical
from pytz import UTC

from nikola.plugin_categories import ShortcodePlugin
from nikola.utils import LocaleBorg


class CalendarPlugin(ShortcodePlugin):
    """Calendar shortcode."""
    name = "ical"

    doc_purpose = "Display ical calendars"
    doc_description = "Format and display ical calendars."
    logger = None
    cmd_options = []

    def set_site(self, site):
        super(CalendarPlugin, self).set_site(site)
        self.site.register_shortcode('calendar', self.handler)

    def handler(self, site=None, data=None, lang=None, file=None, template=None, post=None, days_in_future=None, days_in_past=0):
        if not template:
            template = 'calendar.tmpl'
        deps = self.site.template_system.template_deps(template)

        if file is not None:
            with open(file, 'rb') as inf:
                data = inf.read()
            deps.append(file)
        cal = ical.Calendar.from_ical(data)

        events = []
        for element in cal.walk():
            eventdict = {}
            if element.name == "VEVENT":
                if element.get('summary') is not None:
                    eventdict['summary'] = element.get('summary')
                if element.get('description') is not None:
                    eventdict['description'] = element.get('description')
                if element.get('url') is not None:
                    eventdict['url'] = element.get('url')
                if element.get('dtstart') is not None:
                    eventdict['dtstart'] = element.get('dtstart').dt
                if element.get('dtend') is not None:
                    eventdict['dtend'] = element.get('dtend').dt

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

                    calc_startdate = datetime.now(tz=UTC)
                    calc_startdate -= timedelta(days=int(days_in_past))
                    calc_enddate = datetime.now(tz=UTC)
                    calc_enddate += timedelta(days=int(days_in_future))

                    for entry_calcdate in rules.between(calc_startdate, calc_enddate):
                        new_entry = eventdict.copy()
                        duration = new_entry['dtend'] - new_entry['dtstart']
                        new_entry['dtstart'] = entry_calcdate
                        new_entry['dtend'] = entry_calcdate + duration
                        events.append(new_entry)
                else:
                    events.append(eventdict)

        output = self.site.render_template(
            template,
            None,
            {
                'events': events,
                'lang': LocaleBorg().current_lang,
            })

        return output, deps
