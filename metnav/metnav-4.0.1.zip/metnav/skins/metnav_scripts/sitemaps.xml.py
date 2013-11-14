exist=context.exist
collection=context.portal_metadataNav.getCollection(REQUEST=None).get('collection', '')
query ="""xquery version "1.0";
declare namespace lom="http://ltsc.ieee.org/xsd/LOM";
declare namespace lomfrens="http://pratic.ens-lyon.fr/xsd/LOMFRENS";

<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
	<url>
		<loc>%s</loc>
		<lastmod>{adjust-date-to-timezone(current-date(), ())}</lastmod>
		<changefreq>daily</changefreq>
		<priority>0.8</priority>
	</url>
	{
""" % context.portal_url()
query +="""for $meta in collection('%s')/lom:lom[lom:lifeCycle/lom:contribute[lom:role/lom:value = 'publisher']/lom:date/lom:dateTime <= adjust-date-to-timezone(current-date(), ())]""" % collection
query +="""  let $url := document-uri(root($meta[starts-with(lom:technical/lom:location, 'xmldb:exist')])),
                 $location:=$meta/lom:technical/lom:location,
                 $lastmod := $meta/lom:contribute[lom:role/lom:value='publisher']/lom:date/lom:dateTime/text()
                 order by $lastmod descending empty least
                 return
                    <url>
                        {if(starts-with($location, 'xmldb:exist://'))
                            then
                               <loc>{concat("%s/XML", $url)}</loc>
                            else
                                <loc>{$location}</loc>	
                         }  
                        <lastmod>{$lastmod}</lastmod>
                        <changefreq> yearly </changefreq>
                    </url>
         }
</urlset>""" % context.portal_url()
res = str(exist.query(query))

return """<?xml version="1.0" encoding="utf-8"?>\n""" + res