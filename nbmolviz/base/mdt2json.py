# Copyright 2017 Autodesk Inc.
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


def convert(mol):
    from moldesign import units as u

    js = dict(name=mol.name)

    js['atoms'] = [{'serial': i,
                    'name': atom.name,
                    'elem': atom.elem,
                    'mass_magnitude': float(atom.mass.value_in(u.amu)),
                    'residue_index': atom.residue.index,
                    'residue_name': atom.residue.name,
                    'chain': atom.chain.name}
                   for i, atom in enumerate(mol.atoms)]

    js['bonds'] = [{'atom1_index': bond.a1.index,
                    'atom2_index': bond.a2.index,
                    'bond_order': bond.order}
                   for i, bond in enumerate(mol.bonds)]

    js['residues'] = [{'name': residue.name,
                       'sequence_number': residue.pdbindex,
                       'chain_index': residue.chain.index}
                      for i, residue in enumerate(mol.residues)]

    js['chains'] = [{'name': chain.name,
                     'description': ''}
                    for i, chain in enumerate(mol.chains)]
    return js
