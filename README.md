# nhpcalendar
New Holland Press Wall Calendar Software

This is working code for a Wall Calendar.

It generates the calendar part of a 12 month vertical hanging calendar.

It uses reportlab.org open source software to build the calendar.

moons are stored in moons and use the moon_phases.zip font that is
available online.  It is not free: costs about $25 per published calendar.
The LICENCE for these fonts is published.

I hereby release my contribution of nhpcalendar to the open source community under the terms of the GPL.

holidays are stored in holidays.  One line per holiday.  One holiday per calendar day.

pieces stores the name of each artwork that will be on the facing page per month.

To use this software, install reportlab.org on Python 2.7.*
and run

python calendar.py <month_no>
