pygments-css
============

Pygments_, a Python-based code highlighting tool, comes with a set of builtin styles_ (not css files) for code highlighting. You have to generate a CSS file using the command line. I just figured I'd save someone this work in the future and generate all the CSS files based on the Pygments builtins.

Pretty simple stuff here. These css files were generated using pygmentize
on the command line like so::

    pygmentize -S default -f html > default.css

I'm using a combination of Pygments and Markdown on a django project that has a model with the following save method::

    def save(self):
        self.html = markdown(self.body, 'codehilite')
        super(Entry, self).save()

That's why the CSS styles all have .codehilite in front of them. You should change the .codehilite to work with the style name that you use for your Pygments HTML output.

.. _Pygments: http://pygments.org
.. _styles: http://dev.pocoo.org/projects/pygments/browser/pygments/styles

Theme previews
--------------

To preview the various themes, check out http://richleland.github.io/pygments-css/.
