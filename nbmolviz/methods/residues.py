# Copyright 2016 Autodesk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from moldesign import data


def _repr_markdown_(res):
    return res.markdown_summary()


def markdown_summary(res):
    """ Markdown-formatted information about this residue

    Returns:
        str: markdown-formatted string
    """
    if res.type == 'placeholder':
        return '`%s`'%repr(res)

    if res.molecule is None:
        lines = ["<h3>Residue %s</h3>"%res.name]
    else:
        lines = ["<h3>Residue %s (index %d)</h3>"%(res.name, res.index)]

    if res.type == 'protein':
        lines.append('**Residue codes**: %s / %s'%(res.resname, res.code))
    else:
        lines.append("**Residue code**: %s"%res.resname)
    lines.append('**Type**: %s'%res.type)
    if res.resname in data.RESIDUE_DESCRIPTIONS:
        lines.append('**Description**: %s'%data.RESIDUE_DESCRIPTIONS[res.resname])

    lines.append('**<p>Chain:** %s'%res.chain.name)

    lines.append('**PDB sequence #**: %d'%res.pdbindex)

    terminus = None
    if res.type == 'dna':
        if res.is_3prime_end:
            terminus = "3' end"
        elif res.is_5prime_end:
            terminus = "5' end"
    elif res.type == 'protein':
        if res.is_n_terminal:
            terminus = 'N-terminus'
        elif res.is_c_terminal:
            terminus = 'C-terminus'
    if terminus is not None:
        lines.append('**Terminal residue**: %s of chain %s'%(terminus, res.chain.name))

    if res.molecule is not None:
        lines.append("**Molecule**: %s"%res.molecule.name)

    lines.append("**<p>Number of atoms**: %s"%res.num_atoms)
    if res.backbone:
        lines.append("**Backbone atoms:** %s"%', '.join(x.name for x in res.backbone))
        lines.append("**Sidechain atoms:** %s"%', '.join(x.name for x in res.sidechain))
    else:
        lines.append("**Atom:** %s"%', '.join(x.name for x in res.atoms))

    return '<br>'.join(lines)
