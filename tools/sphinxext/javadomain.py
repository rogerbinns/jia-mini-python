# -*- coding: utf-8 -*-

import re
import string

from docutils import nodes

from sphinx import addnodes
from sphinx.roles import XRefRole
from sphinx.locale import l_, _
from sphinx.domains import Domain, ObjType
from sphinx.directives import ObjectDescription
from sphinx.util.nodes import make_refnode
from sphinx.util.docfields import Field, TypedField

primitives = frozenset(['void', 'boolean', 'byte', 'short', 'int', 'long', 'char', 'float', 'double'])
sig_pattern = re.compile(
    r'''^ (?:([\w.]+(?:\<.+\>)?) \s+)? # return type
          (\w+) \s*                    # method name
          \((.*)\) $                   # arguments
     ''', re.VERBOSE)
arg_pattern = re.compile(
    r'''^ \s* ([\w.]+(?:\<.+\>)?) \s+  # arg type
          (\w+) \s* $                  # arg name
     ''', re.VERBOSE)
fq_classname_pattern = re.compile(r'^([\w.]+\.)?(\w+)(\<.+\>)?$')

class JavaClassDescription(ObjectDescription):
    """ Description of a Java class. """

    def handle_signature(self, fqname, signode):
        m = fq_classname_pattern.match(fqname)
        if m is not None:
            package, classname, generics = m.groups()
        else:
            package, classname, generics = None, fqname, None
        if package is not None and self.env.config.java_show_package:
            signode += addnodes.desc_addname(package, package)
        signode += addnodes.desc_name(classname, classname)
        if generics is not None:
            signode += addnodes.desc_addname(generics, generics)
        if package is not None:
            return package + classname
        else:
            return classname

    def get_index_text(self, name):
        return _('%s (Java class)') % name

    def add_target_and_index(self, name, sig, signode):
        # note target
        if name not in self.state.document.ids:
            signode['names'].append(name)
            signode['ids'].append(name)
            signode['first'] = (not self.names)
            self.state.document.note_explicit_target(signode)
            inv = self.env.domaindata['java']['classes']
            if name in inv:
                self.env.warn(
                    self.env.docname,
                    'duplicate Java class description of %s, ' % name +
                    'other instance in ' + self.env.doc2path(inv[name]),
                    self.lineno)
            inv[name] = self.env.docname

        indextext = self.get_index_text(name)
        if indextext:
            self.indexnode['entries'].append(('single', indextext, name, name))

    def before_content(self):
        ObjectDescription.before_content(self)
        if self.names:
            self.env.temp_data['java:class'] = self.names[0]

class JavaMethodDescription(ObjectDescription):
    """ Description of a Java method. """

    def _parse_type(self, type_name, node):
        if type_name.endswith("..."):
            type_name=type_name[:-3]
        if type_name in primitives:
            node += addnodes.desc_type(type_name, type_name)
        else:
            m = fq_classname_pattern.match(type_name)
            if m is not None:
                package, classname, generics = m.groups()
            else:
                package, classname, generics = None, fqname, None
            if package is not None:
                target = package + classname
            else:
                target = classname
            xref_text = nodes.inline()
            if package is not None and self.env.config.java_show_package:
                xref_text += nodes.Text(package, package)
            xref_text += addnodes.desc_type(classname, classname)
            if generics is not None:
                xref_text += nodes.Text(generics, generics)
            node += addnodes.pending_xref(type_name, xref_text, refdomain='java', reftype='class', reftarget=target)

    def handle_signature(self, sig, signode):
        m = sig_pattern.match(sig)
        if m is None: raise ValueError()
        return_type, method_name, arglist = m.groups()

        arguments = []
        if arglist:
            for arg in arglist.split(','):
                m = arg_pattern.match(arg)
                if m is None: raise ValueError()
                arguments.append(m.groups())

        class_name = self.env.temp_data.get('java:class')
        if not class_name:
            self.env.warn(self.env.docname,
                    'Java method description of %s outside of class is not supported' % sig,
                    self.lineno)
            raise ValueError()

        if return_type is not None: # will be absent for constructors
            self._parse_type(return_type, signode)
        signode += nodes.Text(' ', ' ')
        signode += addnodes.desc_name(method_name, method_name)
        signode += addnodes.desc_parameterlist()
        for type, name in arguments:
            signode[-1] += addnodes.desc_parameter('', '', noemph=True)
            self._parse_type(type, signode[-1][-1])
            signode[-1][-1] += nodes.Text(' ', ' ')
            signode[-1][-1] += nodes.emphasis(name, name)

        return '%s#%s(%s)' % (class_name, method_name, ', '.join(type for type, name in arguments))

    def get_index_text(self, name):
        return _('%s (Java method)') % name

    def add_target_and_index(self, name, sig, signode):
        # note target
        if name not in self.state.document.ids:
            signode['names'].append(name)
            signode['ids'].append(name)
            signode['first'] = (not self.names)
            self.state.document.note_explicit_target(signode)
            inv = self.env.domaindata['java']['methods']
            if name in inv:
                self.env.warn(
                    self.env.docname,
                    'duplicate Java method description of %s, ' % name +
                    'other instance in ' + self.env.doc2path(inv[name]),
                    self.lineno)
            inv[name] = self.env.docname

        indextext = self.get_index_text(name)
        if indextext:
            self.indexnode['entries'].append(('single', indextext, name, name))

class JavaDomain(Domain):
    """Java language domain."""
    name = 'java'
    label = 'Java'
    object_types = {
        'class': ObjType(l_('class'), 'class'),
        'method': ObjType(l_('method'), 'method'),
    }
    directives = {
        'class': JavaClassDescription,
        'method': JavaMethodDescription,
    }
    roles = {
        'class': XRefRole(),
        'method': XRefRole(),
    }
    initial_data = {
        'classes': {},  # fullname -> docname
        'methods': {},  # fullname -> docname
    }

    def clear_doc(self, docname):
        for d in self.data['classes'], self.data['methods']:
            for k, v in d.items():
                if v == docname:
                    del d[k]

    def resolve_xref(self, env, fromdocname, builder, typ, target, node, contnode):
        if '#' in target:
            if target in self.data['methods']:
                docname = self.data['methods'][target]
            else:
                candidates = [k for k in self.data['methods'].iterkeys() if k.endswith('.' + target)]
                if len(candidates) == 1:
                    target = candidates[0]
                    docname = self.data['methods'][target]
                else:
                    return None
        else:
            if target in self.data['classes']:
                docname = self.data['classes'][target]
            else:
                candidates = [k for k in self.data['classes'].iterkeys() if k.endswith('.' + target)]
                if len(candidates) == 1:
                    target = candidates[0]
                    docname = self.data['classes'][target]
                else:
                    return None
        return make_refnode(builder, fromdocname, docname, target, contnode, target)

    def get_objects(self):
        for refname, docname in self.data['classes'].iteritems():
            yield (refname, refname, 'class', docname, refname, 1)
        for refname, docname in self.data['methods'].iteritems():
            yield (refname, refname, 'method', docname, refname, 1)

def setup(app):
    app.add_config_value('java_show_package', False, False)
    app.add_domain(JavaDomain)
