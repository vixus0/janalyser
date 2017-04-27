.headers off
.mode ascii
.separator '' ''

.print '<meta charset=utf-8>'
.print '<title>SAML Library Dependencies</title>'
.print '<link href=report.css rel=stylesheet>'
.print '<script src="list.min.js"></script>'
.print '<script src="report.js"></script>'
.print '<div id=deps>'
.print '<table>'
.print '<thead>'
.print '<tr><th>Class</th><th>Package</th><th>Repo</th><th>Used In</th></tr>'
.print '<tr><th><input class=search placeholder=Search><button class=sort data-sort=name>Sort Name</button><button class=sort data-sort=distinct>Sort Usages</button></th><th><button class=sort data-sort=package>Sort</button></th><th><button class=sort data-sort=repo>Sort</button></th><th></th></tr>'
.print '</thead>'
.print '<tbody class=list>'

select 

printf('<tr data-distinct=%d><td class=name>%s</td>', count(distinct c2.repo), c1.name),
printf('<td class=package>%s</td>', c1.package),
printf('<td class=repo>%s</td>', c1.repo),
printf('<td><ul>%s</ul></td></tr>',
group_concat(
  printf('<li>%s.%s (%s)</li>', c2.package, c2.name, c2.repo), 
  ''
))

from imports as im

inner join classes as c2 on im.class_id = c2.rowid
inner join classes as c1 on im.imports_name = c1.name and im.imports_package = c1.package

where im.imports_package like 'uk.gov.ida.saml%'
group by c1.name, c1.package
order by c1.repo, c1.name, c1.package
;

.print '</tbody>'
.print '</table>'
.print '</div>'
