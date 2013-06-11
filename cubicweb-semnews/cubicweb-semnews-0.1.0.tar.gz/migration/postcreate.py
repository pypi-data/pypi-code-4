# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-semnews postcreate script, executed at instance creation time or when
the cube is added to an existing instance.

You could setup site properties or a workflow here for example.
"""

# Example of site property change
set_property('ui.site-title', "Semnews")
create_entity('Card', content_format=u'text/html', title=u'index',
              content=u"""<div class="hero-unit"><h1>What is it?</h1>
              <p>
              Semnews is a SEMantic NEW System, that allow you to browse information feeds
              in a powerful and complex way.
              It aggregates news from different newspapers, blogs or twitter feeds, and
              extract from the information that are matched again different sources (e.g. NewYork Times,
              Dbpedia, ...) that are used as a reference.
              </p></div>
              """)
create_entity('Card', content_format=u'text/html', title=u'about',
              content=u"""<div class="page-header"><h1>What is it?<small></h1></div>
              <p>
              Semnews is a SEMantic NEW System, that allow you to browse information feeds
              in a powerful and complex way.
              It aggregates news from different newspapers, blogs or twitter feeds, and
              extract from the information that are matched again different sources (e.g. NewYork Times,
              Dbpedia, ...) that are used as a reference.
              </p>

              <p>
              These extracted entities are thus used for:
              <ul>
              <li>Browse the news by thematics and concepts.</li>
              <li>Display various dataviz and datamining results.</li>
              <li>Aggregate the news based on these entities.</li>
              <li>Improve the news understanding by fetching information from other sources
              based on the Semantic Web technologies.</li>
              </ul>
              </p>

              This project is based on different open-source software solutions:
              <ul>
              <li>The <a href='http://scikit-learn.org/stable/'>Scikit-learn</a>
              for the maching learning stuff.</li>
              <li><a href='http://cubicweb.org'>Cubicweb</a> for the CMS and Semantic Web part.</li>
              <li><a href='http://twitter.github.com/bootstrap/'>Bootstrap</a> for CSS and JS.</li>
              </ul>
              </p>

              <p><span class="badge badge-important">Important: This website is still a demo. Be kind !</span></p>
              """)

