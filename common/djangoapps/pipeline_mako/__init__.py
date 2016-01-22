from edxmako.shortcuts import render_to_string

from pipeline.conf import settings
from pipeline.packager import Packager
from pipeline.utils import guess_type
from static_replace import try_staticfiles_lookup

from django.conf import settings as django_settings
from django.contrib.staticfiles.storage import staticfiles_storage


def compressed_css(package_name, raw=False):
    package = settings.PIPELINE_CSS.get(package_name, {})
    if package:
        package = {package_name: package}
    packager = Packager(css_packages=package, js_packages={})

    package = packager.package_for('css', package_name)

    if settings.PIPELINE_ENABLED:
        return render_css(package, package.output_filename, raw=raw)
    else:
        paths = packager.compile(package.paths)
        return render_individual_css(package, paths, raw=raw)


def render_css(package, path, raw=False):
    template_name = package.template_name or "mako/css.html"
    context = package.extra_context

    url = try_staticfiles_lookup(path)
    if raw:
        url += "?raw"
    context.update({
        'type': guess_type(path, 'text/css'),
        'url': url,
    })
    return render_to_string(template_name, context)


def render_individual_css(package, paths, raw=False):
    tags = [render_css(package, path, raw) for path in paths]
    return '\n'.join(tags)


def compressed_js(package_name):
    package = settings.PIPELINE_JS.get(package_name, {})
    if package:
        package = {package_name: package}
    packager = Packager(css_packages={}, js_packages=package)

    package = packager.package_for('js', package_name)

    if settings.PIPELINE_ENABLED:
        return render_js(package, package.output_filename)
    else:
        paths = packager.compile(package.paths)
        templates = packager.pack_templates(package)
        return render_individual_js(package, paths, templates)


def render_js(package, path):
    template_name = package.template_name or "mako/js.html"
    context = package.extra_context
    context.update({
        'type': guess_type(path, 'text/javascript'),
        'url': try_staticfiles_lookup(path)
    })
    return render_to_string(template_name, context)


def render_inline_js(package, js):
    context = package.extra_context
    context.update({
        'source': js
    })
    return render_to_string("mako/inline_js.html", context)


def render_individual_js(package, paths, templates=None):
    tags = [render_js(package, js) for js in paths]
    if templates:
        tags.append(render_inline_js(package, templates))
    return '\n'.join(tags)


def render_require_js_path_overrides(path_overrides):  # pylint: disable=invalid-name
    """Render JavaScript to override default RequireJS paths.

    The Django pipeline appends a hash to JavaScript files,
    so if the JS asset isn't included in the bundle for the page,
    we need to tell RequireJS where to look.

    For example:

        "js/vendor/jquery.min.js" --> "js/vendor/jquery.min.abcd1234"

    We would then add a line in a <script> tag:

        require.paths['jquery'] = 'js/vendor/jquery.min.abcd1234'

    so that any reference to 'jquery' in a JavaScript module
    will cause RequireJS to load '/static/js/vendor/jquery.min.abcd1234.js'

    If running in DEBUG mode (as in devstack), the resolved JavaScript URLs
    won't contain hashes, so the new paths will match the original paths.

    Arguments:
        path_overrides (dict): Mapping of RequireJS module names to
            filesystem paths.

    Returns:
        unicode: The HTML of the <script> tag with the path overrides.

    """
    # Render the <script> tag that overrides the paths defined in `require.paths`
    # Note: We don't use a Mako template to render this because Mako apparently
    # acquires a lock when loading templates, which can lead to a deadlock if
    # this function is called from within another template.
    html = ['<script type="text/javascript">']

    # The rendered <script> tag with overrides should be included *after*
    # the application's RequireJS config, which defines a `require` object.
    # Just in case the `require` object hasn't been loaded, we create a default
    # object.  This will avoid a JavaScript error that might cause the rest of the
    # page to fail; however, it may mean that these overrides won't be available
    # to RequireJS.
    html.extend([
        'var require = require || {};',
        'require.paths = require.paths || [];'
    ])

    # Specify override the base URL to point to STATIC_URL
    html.append(
        "require.baseUrl = '{url}'".format(
            url=django_settings.STATIC_URL
        )
    )

    for module, url_path in path_overrides.iteritems():
        # Calculate the full URL, including any hashes added to the filename by the pipeline.
        # This will also include the base static URL (for example, "/static/") and the
        # ".js" extension.
        actual_url = staticfiles_storage.url(url_path)

        # RequireJS assumes that every file it tries to load has a ".js" extension, so
        # we need to remove ".js" from the module path.
        # RequireJS also already has a base URL set to the base static URL, so we can remove that.
        path = actual_url.replace('.js', '').replace(django_settings.STATIC_URL, '')

        # Add the path override to the inline JavaScript.
        html.append(
            "require.paths['{module}'] = '{path}';".format(
                module=module,
                path=path
            )
        )
    html.append('</script>')
    return "\n".join(html)
