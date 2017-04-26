.headers on
.mode html

.print '<link href="report.css" rel=stylesheet>'
.print '<table>'

select 

c1.name as 'Class',
c1.package as 'Package',
c1.repo as 'Repo',
printf('[UL]%s[/UL]',
group_concat(
  printf('[LI]%s.%s (%s)[/LI]', c2.package, c2.name, c2.repo), 
  ''
)) as 'Used In'

from imports as im

inner join classes as c2 on im.class_id = c2.rowid
inner join classes as c1 on im.imports_name = c1.name and im.imports_package = c1.package

where im.imports_package like 'uk.gov.ida.saml%'
group by c1.name, c1.package
order by c1.repo, c1.name, c1.package
;

.print '</table>'
