#!/usr/bin/env python3
"""Render GitHub's contributionCalendar JSON as a self-contained isometric SVG.

Usage: python3 scripts/render-contributions.py calendar.json assets/contributions-3d.svg
No dependencies. Data comes from GitHub GraphQL, never generated activity.
"""
import html
import json
import math
import pathlib
import sys


def render(payload):
    if payload.get('errors'):
        raise ValueError('GitHub GraphQL returned errors')
    calendar = payload['data']['user']['contributionsCollection']['contributionCalendar']
    weeks = calendar['weeks']
    if not weeks or len(weeks) > 54:
        raise ValueError('Expected up to 54 weeks of contributions')
    days = [day for week in weeks for day in week['contributionDays']]
    peak = max(day['contributionCount'] for day in days)
    active = sum(day['contributionCount'] > 0 for day in days)
    total = calendar['totalContributions']
    date_label = f"{days[0]['date']} — {days[-1]['date']}"
    esc = html.escape
    svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="430" viewBox="0 0 1280 430" role="img" aria-labelledby="title description">
<title id="title">Amit Saini's 3D GitHub contribution landscape</title>
<desc id="description">{total} contributions across {active} active days, {date_label}. Each column represents a day; height reflects contribution count. Peak: {peak} contributions in one day.</desc>
<defs>
  <linearGradient id="bg" x2="1" y2="1"><stop stop-color="#0d1829"/><stop offset="1" stop-color="#080e19"/></linearGradient>
  <linearGradient id="line"><stop stop-color="#173042"/><stop offset=".5" stop-color="#60e5dc"/><stop offset="1" stop-color="#173042"/></linearGradient>
</defs>
<style>
 text {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
 .signal {{ animation: travel 12s linear infinite; }}
 @keyframes travel {{ to {{ stroke-dashoffset: -240; }} }}
 @media (prefers-reduced-motion: reduce) {{ .signal {{ animation: none; }} }}
</style>
<rect width="1280" height="430" rx="16" fill="url(#bg)"/>
<text x="44" y="45" fill="#7e9eae" font-size="14" letter-spacing="3">THE BUILD LOG</text>
<text x="44" y="85" fill="#eef8ff" font-size="29" font-weight="650">A year, one commit at a time.</text>
<text x="1236" y="45" text-anchor="end" fill="#a6bdce" font-size="14">{date_label}</text>
<text x="1236" y="85" text-anchor="end" fill="#62e5dc" font-size="26" font-weight="600">{total:,}<tspan fill="#b0c6d5" font-size="16"> contributions</tspan></text>
<path d="M44 108 H1236" stroke="#1d3044"/>
''']
    # Projection preserves weekday rows and chronological week columns.
    origin_x, origin_y = 140, 160
    sx, sy, depth_x, depth_y = 18.2, 1.65, 10.2, 9.2
    def position(week, weekday):
        return origin_x + week*sx - weekday*depth_x, origin_y + week*sy + weekday*depth_y
    def poly(points, color):
        pts = ' '.join(f'{x:.2f},{y:.2f}' for x,y in points)
        return f'<polygon points="{pts}" fill="{color}"/>'
    a=position(-.7,-.7); b=position(len(weeks)+.3,-.7); c=position(len(weeks)+.3,7.5); d=position(-.7,7.5)
    svg.append(poly([(x,y+7) for x,y in [a,b,c,d]], '#050a13'))
    svg.append(poly([a,b,c,d], '#101d2d'))
    # Back to front for correct occlusion of adjacent columns.
    for wi, week in enumerate(weeks):
        for day in week['contributionDays']:
            count = day['contributionCount']
            if count < 0:
                raise ValueError('Negative contribution count')
            x,y=position(wi,day['weekday'])
            h=3 if count==0 else 5 + 61*math.sqrt(count/max(peak,1))
            level=0 if count==0 else min(4, max(1, math.ceil(count/max(peak,1)*4)))
            top=['#23374a','#226b75','#299e9f','#43c9be','#8af1d5'][level]
            left=['#17283a','#174653','#1a6871','#268a87','#3caa9c'][level]
            right=['#1a2e40','#205661','#25818a','#31a69e','#64cdbc'][level]
            p=(x,y-h); q=(x+15.8,y+1.4-h); r=(x+7.1,y+9.2-h); s=(x-8.7,y+7.8-h)
            svg.append(f'<g><title>{esc(day["date"])}: {count} contributions</title>')
            svg.append(poly([s,r,(r[0],r[1]+h),(s[0],s[1]+h)],left))
            svg.append(poly([q,r,(r[0],r[1]+h),(q[0],q[1]+h)],right))
            svg.append(poly([p,q,r,s],top))
            svg.append('</g>')
    svg.append(f'''<path d="M44 352 H1236" stroke="#203549"/>
<path class="signal" d="M44 352 H1236" stroke="url(#line)" stroke-width="2" stroke-dasharray="48 192"/>
<text x="44" y="389" fill="#aec4d3" font-size="16">{active} active days<tspan dx="28">{peak} contributions on the busiest day</tspan></text>
<text x="992" y="389" fill="#91aabb" font-size="14">Less</text>''')
    for i,color in enumerate(['#23374a','#226b75','#299e9f','#43c9be','#8af1d5']):
        svg.append(f'<rect x="{1034+i*26}" y="375" width="18" height="18" rx="3" fill="{color}"/>')
    svg.append('<text x="1176" y="389" fill="#91aabb" font-size="14">More</text></svg>')
    return '\n'.join(svg)


if __name__ == '__main__':
    source, target = map(pathlib.Path, sys.argv[1:3])
    result = render(json.loads(source.read_text()))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(result)
    print(f'Rendered {target}')
