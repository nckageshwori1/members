/* Event calendar chooser — no login or tracking performed by this website. */
(function () {
  'use strict';
  function escapeICS(value) {
    return String(value || '').replace(/\\/g, '\\\\').replace(/\r?\n/g, '\\n').replace(/,/g, '\\,').replace(/;/g, '\\;');
  }
  function fold(line) {
    const chars = Array.from(line);
    let lines = [], current = '', bytes = 0;
    for (const ch of chars) {
      const n = new TextEncoder().encode(ch).length;
      if (bytes + n > 73) { lines.push(current); current = ' '; bytes = 1; }
      current += ch; bytes += n;
    }
    lines.push(current);
    return lines.join('\r\n');
  }
  function icsFromGoogle(url) {
    const u = new URL(url);
    if (u.hostname !== 'calendar.google.com') throw Error('Invalid calendar URL');
    const dates = (u.searchParams.get('dates') || '').split('/');
    if (dates.length !== 2 || !dates.every(x => /^\d{8}(T\d{6}Z)?$/.test(x))) throw Error('Invalid event dates');
    const allDay = dates[0].length === 8;
    const stamp = new Date().toISOString().replace(/[-:]/g, '').replace(/\.\d{3}Z$/, 'Z');
    const fields = [
      'BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//NC Ward 1//Event Reminder//NE', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
      'BEGIN:VEVENT', 'UID:' + crypto.randomUUID() + '@nckageshwori1.github.io', 'DTSTAMP:' + stamp,
      'DTSTART' + (allDay ? ';VALUE=DATE:' : ':') + dates[0],
      'DTEND' + (allDay ? ';VALUE=DATE:' : ':') + dates[1],
      'SUMMARY:' + escapeICS(u.searchParams.get('text')),
      'DESCRIPTION:' + escapeICS(u.searchParams.get('details')),
      'LOCATION:' + escapeICS(u.searchParams.get('location'))
    ];
    if (!allDay) {
      for (const [trigger, label] of [['-P1D', '१ दिन अगाडि'], ['-PT1H', '१ घण्टा अगाडि']]) {
        fields.push('BEGIN:VALARM', 'ACTION:DISPLAY', 'DESCRIPTION:' + escapeICS(label + ' — ' + (u.searchParams.get('text') || 'कार्यक्रम')), 'TRIGGER:' + trigger, 'END:VALARM');
      }
    } else {
      fields.push('BEGIN:VALARM', 'ACTION:DISPLAY', 'DESCRIPTION:कार्यक्रम सम्झना', 'TRIGGER:-P1D', 'END:VALARM');
    }
    fields.push('END:VEVENT', 'END:VCALENDAR');
    return fields.map(fold).join('\r\n') + '\r\n';
  }
  function open(url) {
    if (!url) return;
    document.getElementById('ncCalendarOverlay')?.remove();
    const overlay = document.createElement('div');
    overlay.id = 'ncCalendarOverlay';
    overlay.setAttribute('role', 'dialog'); overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', 'कार्यक्रम क्यालेन्डर विकल्प');
    overlay.style.cssText = 'position:fixed;inset:0;z-index:2147483000;background:#0d203b99;display:flex;align-items:center;justify-content:center;padding:16px';
    const panel = document.createElement('div');
    panel.style.cssText = 'width:min(100%,420px);background:#fff;border-radius:18px;padding:22px;color:#153352;font-family:inherit;box-shadow:0 16px 60px #0003;line-height:1.7';
    panel.innerHTML = '<div style="display:flex;justify-content:space-between;align-items:center;gap:12px"><strong style="font-size:19px">📅 कार्यक्रम सम्झना</strong><button type="button" data-cal-close aria-label="बन्द गर्नुहोस्" style="border:0;background:#eef3f8;border-radius:9px;padding:6px 11px;cursor:pointer">✕</button></div>' +
      '<p style="font-size:13px;margin:12px 0;color:#526579">कुन क्यालेन्डरमा कार्यक्रम सुरक्षित गर्ने?</p>' +
      '<button type="button" data-cal-google style="width:100%;padding:13px;border:0;border-radius:11px;background:#0d315d;color:white;font:inherit;font-weight:700;cursor:pointer;margin-bottom:10px">Google Calendar मा राख्नुहोस् ↗</button>' +
      '<button type="button" data-cal-phone style="width:100%;padding:13px;border:1px solid #c8d8e7;border-radius:11px;background:#f2f7fb;color:#0d315d;font:inherit;font-weight:700;cursor:pointer">📱 फोनको Calendar (.ics)</button>' +
      '<p style="font-size:12px;color:#53697e;margin:14px 0 0">फोनको Calendar फाइलमा समय तोकिएको कार्यक्रमका लागि १ दिन र १ घण्टा अगाडिको Reminder समावेश छ। Google Calendar मा Save गरेपछि Reminder जाँच्नुहोस्। सूचना आउन Calendar एप, Account Sync र Notification अनुमति सक्रिय हुनुपर्छ।</p>';
    overlay.appendChild(panel); document.body.appendChild(overlay);
    const close = () => overlay.remove();
    overlay.addEventListener('click', e => { if (e.target === overlay) close(); });
    panel.querySelector('[data-cal-close]').addEventListener('click', close);
    panel.querySelector('[data-cal-google]').addEventListener('click', () => { window.open(url, '_blank', 'noopener,noreferrer'); close(); });
    panel.querySelector('[data-cal-phone]').addEventListener('click', () => {
      try {
        const blob = new Blob([icsFromGoogle(url)], {type:'text/calendar;charset=utf-8'});
        const a = document.createElement('a'), href = URL.createObjectURL(blob);
        a.href = href; a.download = 'NC-Program-Reminder.ics'; document.body.appendChild(a); a.click(); a.remove();
        setTimeout(() => URL.revokeObjectURL(href), 15000); close();
      } catch (error) { alert('Calendar फाइल तयार गर्न सकिएन। कृपया Google Calendar प्रयोग गर्नुहोस्।'); }
    });
    panel.querySelector('[data-cal-close]').focus();
  }
  window.NCEventCalendar = Object.freeze({open});
})();
