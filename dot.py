import re
from pyang import plugin, statements, util, error

# TODO: Need to figure out what to do when multiple revisions
#       of the same module is present

def pyang_plugin_init():
    plugin.register_plugin(DotPlugin())

class DotPlugin(plugin.PyangPlugin):
    def add_output_format(self, fmts):
        self.multiple_modules = True
        fmts['dot'] = self

    def setup_fmt(self, ctx):
        ctx.implicit_errors = False

    def emit(self, ctx, modules, fd):
        # Require error-free modules
        modulenames = [m.arg for m in modules]
        for (epos, etag, eargs) in ctx.errors:
            if (epos.top.arg in modulenames and
                error.is_error(error.err_level(etag))):
                raise error.EmitError("%s contains errors" % epos.top.arg)

        emit_dot(ctx, modules, fd)

def emit_dot(ctx, modules, fd):
	seen = []

	fd.write("digraph \"modules-graph\" {\n")

	for module in modules:
		modname = module.arg
		modrev = util.get_latest_revision(module)
		modid = "%s@%s" % (modname, modrev)

		if modid in seen:
			# Ignoring duplicate modules
			continue
		else:
			seen.append(modid)
			fd.write("\t\"%s\"\n" % (modid))

		imps = module.search('import')
		if imps:
			for imp in imps:
				if imp.search('revision-date'):
					date = imp.search_one('revision-date').arg
					fd.write("\t\"%s\" -> \"%s\" [label=\"imports by revision: %s\"]\n" % (modname, imp.arg, date))
				else:
					fd.write("\t\"%s\" -> \"%s\" [label=imports]\n" % (modname, imp.arg))

		subs = module.search('include')
		if subs:
			for sub in subs:
				if sub.search('revision-date'):
					date = sub.search_one('revision-date').arg
					fd.write("\t\"%s\" -> \"%s\" [label=\"includes by revision: %s\"]\n" % (modname, sub.arg, date))
				else:
					fd.write("\t\"%s\" -> \"%s\" [label=includes]\n" % (modname, sub.arg))

	fd.write("}")


